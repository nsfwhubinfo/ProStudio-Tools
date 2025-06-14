#!/usr/bin/env python3
"""
ProStudio Production API Server
===============================

High-performance production server with monitoring, caching, and scaling.
"""

import os
import sys
import time
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from functools import wraps
import threading
import signal

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Flask and extensions
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

# Monitoring
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import psutil

# Configuration
from config.production import Config

# ProStudio components
from core.content_engine import ContentEngine
from core.content_types import Platform, ContentType
from core.acceleration.redis_cache import RedisContentCache
from core.acceleration.distributed_engine import DistributedContentEngine

# Setup JSON logging
if Config.LOG_FORMAT == 'json':
    from pythonjsonlogger import jsonlogger
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter()
    logHandler.setFormatter(formatter)
    logging.root.addHandler(logHandler)
    logging.root.setLevel(Config.LOG_LEVEL)

logger = logging.getLogger(__name__)

# Metrics
request_count = Counter('prostudio_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('prostudio_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
active_requests = Gauge('prostudio_active_requests', 'Active requests')
generation_time = Histogram('prostudio_generation_time_seconds', 'Content generation time', ['platform', 'content_type'])
cache_hits = Counter('prostudio_cache_hits_total', 'Cache hits')
cache_misses = Counter('prostudio_cache_misses_total', 'Cache misses')
error_count = Counter('prostudio_errors_total', 'Total errors', ['error_type'])

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=Config.ALLOWED_ORIGINS)

# Global instances
engine = None
cache = None
distributed_engine = None


def initialize_components():
    """Initialize all ProStudio components"""
    global engine, cache, distributed_engine
    
    logger.info("Initializing ProStudio components...")
    
    # Initialize main engine
    engine = ContentEngine(Config.get_engine_config())
    engine.initialize()
    logger.info("Content engine initialized")
    
    # Initialize cache
    if Config.ENABLE_CACHING:
        try:
            cache = RedisContentCache({
                'host': Config.REDIS_HOST,
                'port': Config.REDIS_PORT,
                'password': Config.REDIS_PASSWORD,
                'ttl_seconds': Config.REDIS_TTL
            })
            logger.info("Redis cache initialized")
        except Exception as e:
            logger.warning(f"Redis cache initialization failed: {e}")
            cache = None
    
    # Initialize distributed engine
    if Config.ENABLE_DISTRIBUTED:
        try:
            distributed_engine = DistributedContentEngine({
                'backend': 'ray' if Config.RAY_CONFIG['num_cpus'] > 1 else 'threading',
                'num_workers': Config.ENGINE_CONFIG['max_workers']
            })
            logger.info("Distributed engine initialized")
        except Exception as e:
            logger.warning(f"Distributed engine initialization failed: {e}")
            distributed_engine = None


def require_api_key(f):
    """Decorator to require API key for endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if Config.API_KEY:
            provided_key = request.headers.get('X-API-Key')
            if provided_key != Config.API_KEY:
                return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function


def track_metrics(f):
    """Decorator to track request metrics"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        active_requests.inc()
        
        try:
            response = f(*args, **kwargs)
            status = response[1] if isinstance(response, tuple) else 200
            return response
        except Exception as e:
            status = 500
            raise
        finally:
            duration = time.time() - start_time
            active_requests.dec()
            
            endpoint = request.endpoint or 'unknown'
            method = request.method
            
            request_count.labels(method=method, endpoint=endpoint, status=status).inc()
            request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    return decorated_function


@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler"""
    if isinstance(error, HTTPException):
        response = error.get_response()
        response.data = json.dumps({
            'error': error.name,
            'message': error.description,
        })
        response.content_type = "application/json"
        return response
    
    # Log unexpected errors
    logger.error(f"Unhandled error: {error}", exc_info=True)
    error_count.labels(error_type=type(error).__name__).inc()
    
    # Send to Sentry if configured
    if Config.SENTRY_DSN:
        import sentry_sdk
        sentry_sdk.capture_exception(error)
    
    return jsonify({
        'error': 'Internal server error',
        'message': str(error) if app.debug else 'An error occurred'
    }), 500


@app.before_request
def before_request():
    """Pre-request processing"""
    g.start_time = time.time()
    g.request_id = request.headers.get('X-Request-ID', str(time.time()))
    
    # Log request
    logger.info('Request started', extra={
        'request_id': g.request_id,
        'method': request.method,
        'path': request.path,
        'ip': request.remote_addr
    })


@app.after_request
def after_request(response):
    """Post-request processing"""
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        response.headers['X-Response-Time'] = str(duration)
        
        # Log response
        logger.info('Request completed', extra={
            'request_id': g.request_id,
            'status': response.status_code,
            'duration': duration
        })
    
    return response


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'components': {
            'engine': 'ok' if engine else 'not initialized',
            'cache': 'ok' if cache and cache.redis_available else 'not available',
            'distributed': 'ok' if distributed_engine else 'not available'
        },
        'metrics': {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'active_requests': active_requests._value.get()
        }
    }
    
    # Check if any component is unhealthy
    if not engine or (Config.ENABLE_CACHING and not cache):
        health_status['status'] = 'degraded'
    
    return jsonify(health_status), 200 if health_status['status'] == 'healthy' else 503


@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()


@app.route('/generate', methods=['POST'])
@track_metrics
@require_api_key
def generate():
    """Generate single content item"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'concept' not in data:
            return jsonify({'error': 'Missing required field: concept'}), 400
        
        concept = data['concept'][:Config.MAX_CONTENT_LENGTH]
        platform = data.get('platform', 'TIKTOK')
        content_type = data.get('content_type', 'VIDEO_SHORT')
        
        # Check cache first
        if cache:
            cached_content = cache.get(concept, platform, content_type)
            if cached_content:
                cache_hits.inc()
                logger.info(f"Cache hit for concept: {concept}")
                return jsonify({
                    'id': cached_content.id,
                    'concept': concept,
                    'platform': platform,
                    'content_type': content_type,
                    'generation_time_ms': 0.5,  # Cache hit
                    'predicted_engagement': cached_content.optimization.predicted_engagement,
                    'viral_coefficient': cached_content.optimization.viral_coefficient,
                    'cached': True
                })
            else:
                cache_misses.inc()
        
        # Generate content
        start_time = time.time()
        content = engine.generate_content(
            concept=concept,
            content_type=ContentType[content_type],
            platform=Platform[platform]
        )
        gen_time = time.time() - start_time
        
        # Track generation time
        generation_time.labels(platform=platform, content_type=content_type).observe(gen_time)
        
        # Cache the result
        if cache:
            cache.set(concept, platform, content_type, content)
        
        # Build response
        response_data = {
            'id': content.id,
            'concept': concept,
            'platform': platform,
            'content_type': content_type,
            'generation_time_ms': gen_time * 1000,
            'predicted_engagement': content.optimization.predicted_engagement,
            'viral_coefficient': content.optimization.viral_coefficient,
            'cached': False
        }
        
        # Add metadata if requested
        if data.get('include_metadata', False):
            response_data['metadata'] = content.metadata
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Generation error: {e}", exc_info=True)
        error_count.labels(error_type='generation_error').inc()
        return jsonify({'error': str(e)}), 500


@app.route('/batch', methods=['POST'])
@track_metrics
@require_api_key
def batch_generate():
    """Batch content generation"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'concepts' not in data:
            return jsonify({'error': 'Missing required field: concepts'}), 400
        
        concepts = data['concepts'][:Config.MAX_BATCH_SIZE]
        platforms = data.get('platforms', ['TIKTOK'])
        content_types = data.get('content_types')
        
        # Use distributed engine if available
        if distributed_engine and len(concepts) > 10:
            logger.info(f"Using distributed engine for {len(concepts)} concepts")
            start_time = time.time()
            
            results = distributed_engine.distribute_batch(
                concepts, platforms, content_types
            )
            
            total_time = time.time() - start_time
            
            return jsonify({
                'results': results,
                'count': len(results),
                'total_time_ms': total_time * 1000,
                'distributed': True
            })
        
        # Fall back to sequential generation
        results = []
        start_time = time.time()
        
        for i, concept in enumerate(concepts):
            for platform in platforms:
                content_type = content_types[i] if content_types else 'VIDEO_SHORT'
                
                # Check cache
                if cache:
                    cached = cache.get(concept, platform, content_type)
                    if cached:
                        results.append({
                            'concept': concept,
                            'platform': platform,
                            'cached': True
                        })
                        continue
                
                # Generate
                content = engine.generate_content(
                    concept=concept,
                    content_type=ContentType[content_type],
                    platform=Platform[platform]
                )
                
                results.append({
                    'id': content.id,
                    'concept': concept,
                    'platform': platform,
                    'engagement': content.optimization.predicted_engagement,
                    'cached': False
                })
                
                # Cache result
                if cache:
                    cache.set(concept, platform, content_type, content)
        
        total_time = time.time() - start_time
        
        return jsonify({
            'results': results,
            'count': len(results),
            'total_time_ms': total_time * 1000,
            'distributed': False
        })
        
    except Exception as e:
        logger.error(f"Batch generation error: {e}", exc_info=True)
        error_count.labels(error_type='batch_error').inc()
        return jsonify({'error': str(e)}), 500


@app.route('/stats', methods=['GET'])
def stats():
    """Server statistics"""
    stats = {
        'uptime': time.time() - app.start_time,
        'total_requests': sum(request_count._value.values()),
        'active_requests': active_requests._value.get(),
        'cache_stats': cache.get_stats() if cache else None,
        'system': {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': {
                'percent': psutil.virtual_memory().percent,
                'available_gb': psutil.virtual_memory().available / (1024**3)
            },
            'disk': {
                'percent': psutil.disk_usage('/').percent,
                'free_gb': psutil.disk_usage('/').free / (1024**3)
            }
        }
    }
    
    return jsonify(stats)


def graceful_shutdown(signum, frame):
    """Handle graceful shutdown"""
    logger.info("Received shutdown signal, cleaning up...")
    
    if distributed_engine:
        distributed_engine.shutdown()
    
    if cache:
        cache.close()
    
    logger.info("Cleanup complete, exiting")
    sys.exit(0)


def main():
    """Main entry point"""
    # Register signal handlers
    signal.signal(signal.SIGTERM, graceful_shutdown)
    signal.signal(signal.SIGINT, graceful_shutdown)
    
    # Initialize Sentry if configured
    if Config.SENTRY_DSN:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        
        sentry_sdk.init(
            dsn=Config.SENTRY_DSN,
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.1,
            environment=Config.ENV
        )
    
    # Initialize components
    initialize_components()
    
    # Store start time
    app.start_time = time.time()
    
    # Log startup
    logger.info("ProStudio API Server starting", extra={
        'config': {
            'workers': Config.API_WORKERS,
            'gpu_enabled': Config.ENABLE_GPU,
            'cache_enabled': Config.ENABLE_CACHING,
            'distributed_enabled': Config.ENABLE_DISTRIBUTED
        }
    })
    
    # Run server
    if os.getenv('PROSTUDIO_ENV') == 'production':
        # Production: Use gunicorn or other WSGI server
        logger.info(f"Running in production mode on port {Config.API_PORT}")
        # Gunicorn will handle the actual serving
    else:
        # Development
        app.run(
            host=Config.API_HOST,
            port=Config.API_PORT,
            debug=True,
            threaded=True
        )


if __name__ == '__main__':
    main()