#!/usr/bin/env python3
"""
ProStudio API Server
====================

REST API server for ProStudio content generation.
"""

import os
import sys
import json
import time
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try different web frameworks
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    FRAMEWORK = "flask"
except ImportError:
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
        import uvicorn
        FRAMEWORK = "fastapi"
    except ImportError:
        FRAMEWORK = "http"
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import urllib.parse

# Import ProStudio components
from core.content_engine import ContentEngine
from core.content_engine.content_types import Platform, ContentType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Request/Response models
@dataclass
class GenerateRequest:
    concept: str
    platform: str = "TIKTOK"
    content_type: str = "VIDEO_SHORT"
    optimize: bool = True


@dataclass
class BatchRequest:
    concepts: List[str]
    platforms: List[str]
    content_types: Optional[List[str]] = None
    count: int = 10


@dataclass
class GenerateResponse:
    id: str
    concept: str
    platform: str
    content_type: str
    generation_time_ms: float
    predicted_engagement: float
    viral_coefficient: float
    script: Optional[str] = None
    hashtags: Optional[List[str]] = None
    timestamp: str = None


# Initialize engine
engine_config = {
    'enable_performance_mode': True,
    'enable_fa_cms': True,
    'optimization_iterations': 2,
    'enable_gpu': os.getenv('ENABLE_GPU', 'false').lower() == 'true',
    'enable_caching': os.getenv('REDIS_HOST') is not None
}

engine = ContentEngine(engine_config)
engine.initialize()
logger.info(f"ProStudio engine initialized with config: {engine_config}")


if FRAMEWORK == "flask":
    # Flask implementation
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'version': '1.0.0',
            'engine': 'ProStudio SDK',
            'framework': 'flask'
        })
    
    @app.route('/generate', methods=['POST'])
    def generate():
        try:
            data = request.get_json()
            req = GenerateRequest(**data)
            
            # Generate content
            start_time = time.time()
            content = engine.generate_content(
                concept=req.concept,
                content_type=ContentType[req.content_type],
                platform=Platform[req.platform]
            )
            generation_time = (time.time() - start_time) * 1000
            
            # Build response
            response = GenerateResponse(
                id=content.id,
                concept=req.concept,
                platform=req.platform,
                content_type=req.content_type,
                generation_time_ms=generation_time,
                predicted_engagement=content.optimization.predicted_engagement,
                viral_coefficient=content.optimization.viral_coefficient,
                script=content.metadata.get('script'),
                hashtags=content.metadata.get('hashtags'),
                timestamp=datetime.now().isoformat()
            )
            
            return jsonify(asdict(response))
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/batch', methods=['POST'])
    def batch_generate():
        try:
            data = request.get_json()
            req = BatchRequest(**data)
            
            results = []
            start_time = time.time()
            
            for i, concept in enumerate(req.concepts[:req.count]):
                for platform in req.platforms:
                    content_type = req.content_types[i] if req.content_types else "VIDEO_SHORT"
                    
                    content = engine.generate_content(
                        concept=concept,
                        content_type=ContentType[content_type],
                        platform=Platform[platform]
                    )
                    
                    results.append({
                        'id': content.id,
                        'concept': concept,
                        'platform': platform,
                        'engagement': content.optimization.predicted_engagement
                    })
            
            total_time = (time.time() - start_time) * 1000
            
            return jsonify({
                'results': results,
                'count': len(results),
                'total_time_ms': total_time,
                'avg_time_ms': total_time / len(results) if results else 0
            })
            
        except Exception as e:
            logger.error(f"Batch generation error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/stats', methods=['GET'])
    def stats():
        # Get cache stats if available
        cache_stats = {}
        try:
            from core.acceleration.redis_cache import RedisContentCache
            cache = RedisContentCache()
            cache_stats = cache.get_stats()
        except:
            pass
        
        return jsonify({
            'engine_config': engine_config,
            'cache_stats': cache_stats,
            'server_uptime': time.time()
        })
    

elif FRAMEWORK == "fastapi":
    # FastAPI implementation
    app = FastAPI(title="ProStudio API", version="1.0.0")
    
    class GenerateRequestModel(BaseModel):
        concept: str
        platform: str = "TIKTOK"
        content_type: str = "VIDEO_SHORT"
        optimize: bool = True
    
    class BatchRequestModel(BaseModel):
        concepts: List[str]
        platforms: List[str]
        content_types: Optional[List[str]] = None
        count: int = 10
    
    @app.get("/health")
    def health():
        return {
            'status': 'healthy',
            'version': '1.0.0',
            'engine': 'ProStudio SDK',
            'framework': 'fastapi'
        }
    
    @app.post("/generate")
    def generate(req: GenerateRequestModel):
        try:
            start_time = time.time()
            content = engine.generate_content(
                concept=req.concept,
                content_type=ContentType[req.content_type],
                platform=Platform[req.platform]
            )
            generation_time = (time.time() - start_time) * 1000
            
            return {
                'id': content.id,
                'concept': req.concept,
                'platform': req.platform,
                'content_type': req.content_type,
                'generation_time_ms': generation_time,
                'predicted_engagement': content.optimization.predicted_engagement,
                'viral_coefficient': content.optimization.viral_coefficient,
                'script': content.metadata.get('script'),
                'hashtags': content.metadata.get('hashtags'),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    

else:
    # Basic HTTP server implementation
    class ProStudioHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {
                    'status': 'healthy',
                    'version': '1.0.0',
                    'engine': 'ProStudio SDK',
                    'framework': 'http.server'
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.end_headers()
        
        def do_POST(self):
            if self.path == '/generate':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode())
                
                try:
                    start_time = time.time()
                    content = engine.generate_content(
                        concept=data['concept'],
                        content_type=ContentType[data.get('content_type', 'VIDEO_SHORT')],
                        platform=Platform[data.get('platform', 'TIKTOK')]
                    )
                    generation_time = (time.time() - start_time) * 1000
                    
                    response = {
                        'id': content.id,
                        'concept': data['concept'],
                        'platform': data.get('platform', 'TIKTOK'),
                        'content_type': data.get('content_type', 'VIDEO_SHORT'),
                        'generation_time_ms': generation_time,
                        'predicted_engagement': content.optimization.predicted_engagement,
                        'viral_coefficient': content.optimization.viral_coefficient,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                    
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': str(e)}).encode())
            else:
                self.send_response(404)
                self.end_headers()
        
        def log_message(self, format, *args):
            logger.info(f"{self.address_string()} - {format % args}")


def main():
    """Run the API server"""
    port = int(os.getenv('PORT', 8000))
    
    print(f"""
    🚀 ProStudio API Server
    =======================
    
    Framework: {FRAMEWORK}
    Port: {port}
    
    Endpoints:
    - GET  /health      - Health check
    - POST /generate    - Generate single content
    - POST /batch       - Batch generation
    - GET  /stats       - Server statistics
    
    Example:
    curl -X POST http://localhost:{port}/generate \\
      -H "Content-Type: application/json" \\
      -d '{{"concept": "AI productivity tips", "platform": "TIKTOK"}}'
    
    Starting server...
    """)
    
    if FRAMEWORK == "flask":
        app.run(host='0.0.0.0', port=port, debug=False)
    elif FRAMEWORK == "fastapi":
        uvicorn.run(app, host='0.0.0.0', port=port)
    else:
        server = HTTPServer(('0.0.0.0', port), ProStudioHandler)
        logger.info(f"Server running on http://0.0.0.0:{port}")
        server.serve_forever()


if __name__ == "__main__":
    main()