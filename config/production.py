"""
ProStudio Production Configuration
==================================
"""

import os
from typing import Dict, Any

class ProductionConfig:
    """Production configuration for ProStudio"""
    
    # API Configuration
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 8000))
    API_WORKERS = int(os.getenv('API_WORKERS', 4))
    API_THREADS = int(os.getenv('API_THREADS', 2))
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', 120))
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    API_KEY = os.getenv('API_KEY', None)
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')
    
    # Redis Configuration
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    REDIS_MAX_CONNECTIONS = int(os.getenv('REDIS_MAX_CONNECTIONS', 50))
    REDIS_TTL = int(os.getenv('REDIS_TTL', 3600))  # 1 hour
    
    # Performance Settings
    ENABLE_GPU = os.getenv('ENABLE_GPU', 'false').lower() == 'true'
    ENABLE_CACHING = os.getenv('ENABLE_CACHING', 'true').lower() == 'true'
    ENABLE_DISTRIBUTED = os.getenv('ENABLE_DISTRIBUTED', 'true').lower() == 'true'
    
    # Engine Configuration
    ENGINE_CONFIG = {
        'enable_performance_mode': True,
        'enable_fa_cms': True,
        'optimization_iterations': int(os.getenv('OPTIMIZATION_ITERATIONS', 3)),
        'enable_gpu': ENABLE_GPU,
        'enable_caching': ENABLE_CACHING,
        'batch_size': int(os.getenv('BATCH_SIZE', 32)),
        'max_workers': int(os.getenv('MAX_WORKERS', 4)),
    }
    
    # Ray Configuration
    RAY_CONFIG = {
        'num_cpus': int(os.getenv('RAY_NUM_CPUS', 4)),
        'num_gpus': int(os.getenv('RAY_NUM_GPUS', 0)),
        'object_store_memory': int(os.getenv('RAY_OBJECT_STORE_MEMORY', 2_000_000_000)),
        'dashboard_host': '0.0.0.0',
        'dashboard_port': 8265,
    }
    
    # Database Configuration (optional)
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///prostudio.db')
    
    # Monitoring
    ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'true').lower() == 'true'
    METRICS_PORT = int(os.getenv('METRICS_PORT', 9090))
    SENTRY_DSN = os.getenv('SENTRY_DSN', None)
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = 'json'  # json or text
    LOG_FILE = os.getenv('LOG_FILE', 'logs/prostudio.log')
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    RATE_LIMIT_DEFAULT = os.getenv('RATE_LIMIT_DEFAULT', '100/hour')
    
    # Content Generation Limits
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 10000))
    MAX_BATCH_SIZE = int(os.getenv('MAX_BATCH_SIZE', 100))
    MAX_GENERATION_TIME = int(os.getenv('MAX_GENERATION_TIME', 30))  # seconds
    
    @classmethod
    def get_engine_config(cls) -> Dict[str, Any]:
        """Get engine configuration"""
        return cls.ENGINE_CONFIG.copy()
    
    @classmethod
    def get_redis_url(cls) -> str:
        """Get Redis connection URL"""
        auth = f":{cls.REDIS_PASSWORD}@" if cls.REDIS_PASSWORD else ""
        return f"redis://{auth}{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        issues = []
        
        if cls.SECRET_KEY == 'your-secret-key-here':
            issues.append("SECRET_KEY must be set for production")
        
        if cls.API_KEY is None:
            issues.append("API_KEY should be set for production API security")
        
        if cls.SENTRY_DSN is None:
            issues.append("SENTRY_DSN recommended for error tracking")
        
        if issues:
            print("⚠️  Configuration warnings:")
            for issue in issues:
                print(f"   - {issue}")
        
        return len(issues) == 0


# Development configuration (for comparison)
class DevelopmentConfig(ProductionConfig):
    """Development configuration"""
    
    API_WORKERS = 1
    API_THREADS = 1
    
    ENGINE_CONFIG = {
        'enable_performance_mode': False,
        'enable_fa_cms': True,
        'optimization_iterations': 1,
        'enable_gpu': False,
        'enable_caching': False,
    }
    
    RATE_LIMIT_ENABLED = False
    LOG_LEVEL = 'DEBUG'
    LOG_FORMAT = 'text'


# Select configuration based on environment
ENV = os.getenv('PROSTUDIO_ENV', 'development')

if ENV == 'production':
    Config = ProductionConfig
else:
    Config = DevelopmentConfig

# Validate on import
Config.validate()