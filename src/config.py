"""
Configuration management for Contract Analyzer Dashboard
Handles environment variables with sensible defaults
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class with all settings"""
    
    # === FLASK CONFIGURATION ===
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', os.getenv('FLASK_DEBUG', 'true')).lower() == 'true'
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', os.getenv('FLASK_PORT', '5000')))
    
    # === DIRECTORY PATHS ===
    BASE_DIR = Path(__file__).parent.parent  # Project root
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'data/uploads')
    TEMPLATES_FOLDER = os.getenv('TEMPLATES_FOLDER', 'data/templates')
    REPORTS_FOLDER = os.getenv('REPORTS_FOLDER', 'data/reports')
    STATIC_FOLDER = os.getenv('STATIC_FOLDER', 'static')
    TEMPLATE_FOLDER = os.getenv('TEMPLATE_FOLDER', 'templates')
    
    # === FILE UPLOAD LIMITS ===
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
    ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS', 'docx').split(',')
    MAX_FILENAME_LENGTH = int(os.getenv('MAX_FILENAME_LENGTH', '255'))
    
    # === LLM PROVIDER CONFIGURATION ===
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openai')  # Only 'openai' supported
    
    # === OPENAI CONFIGURATION ===
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')  # Default to recommended model
    OPENAI_TIMEOUT = int(os.getenv('OPENAI_TIMEOUT', '30'))
    OPENAI_MAX_RETRIES = int(os.getenv('OPENAI_MAX_RETRIES', '3'))
    OPENAI_RETRY_DELAY = int(os.getenv('OPENAI_RETRY_DELAY', '2'))
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    
    # === LLM PARAMETERS ===
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.1'))
    LLM_TOP_P = float(os.getenv('LLM_TOP_P', '0.9'))
    LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '512'))  # ⚡ Reduced for speed
    
    # === 🚀 PERFORMANCE OPTIMIZATIONS ===
    LLM_BATCH_SIZE = int(os.getenv('LLM_BATCH_SIZE', '10'))  # Changes per API call
    LLM_USE_FAST_MODEL = os.getenv('LLM_USE_FAST_MODEL', 'true').lower() == 'true'
    LLM_FAST_MODEL = os.getenv('LLM_FAST_MODEL', 'gpt-4o-mini')
    LLM_TIMEOUT_OPTIMIZED = int(os.getenv('LLM_TIMEOUT_OPTIMIZED', '15'))  # Faster timeout
    LLM_MAX_PROMPT_LENGTH = int(os.getenv('LLM_MAX_PROMPT_LENGTH', '8000'))  # Truncate long prompts
    
    # === SECURITY SETTINGS ===
    SECURE_FILENAME_ENABLED = os.getenv('SECURE_FILENAME_ENABLED', 'true').lower() == 'true'
    PATH_TRAVERSAL_PROTECTION = os.getenv('PATH_TRAVERSAL_PROTECTION', 'true').lower() == 'true'
    FILE_VALIDATION_ENABLED = os.getenv('FILE_VALIDATION_ENABLED', 'true').lower() == 'true'
    CONTENT_TYPE_VALIDATION = os.getenv('CONTENT_TYPE_VALIDATION', 'true').lower() == 'true'
    
    # === LOGGING CONFIGURATION ===
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'output/logs/dashboard.log')
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # === ANALYSIS SETTINGS ===
    SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.5'))
    SIGNIFICANT_CHANGES_THRESHOLD = int(os.getenv('SIGNIFICANT_CHANGES_THRESHOLD', '10'))
    ANALYSIS_TIMEOUT = int(os.getenv('ANALYSIS_TIMEOUT', '300'))
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', '10'))
    
    # === PERFORMANCE SETTINGS ===
    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', '3600'))
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
    CONNECTION_POOL_SIZE = int(os.getenv('CONNECTION_POOL_SIZE', '10'))
    
    # === MONITORING ===
    HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', '30'))
    METRICS_ENABLED = os.getenv('METRICS_ENABLED', 'true').lower() == 'true'
    MONITORING_ENDPOINT = os.getenv('MONITORING_ENDPOINT', '/api/health')
    
    # === DASHBOARD SETTINGS ===
    DASHBOARD_TITLE = os.getenv('DASHBOARD_TITLE', 'Contract Analyzer Dashboard')
    DASHBOARD_THEME = os.getenv('DASHBOARD_THEME', 'auto')
    AUTO_REFRESH_INTERVAL = int(os.getenv('AUTO_REFRESH_INTERVAL', '30000'))
    PAGINATION_SIZE = int(os.getenv('PAGINATION_SIZE', '20'))
    
    # === EXTERNAL SERVICES ===
    BACKUP_ENABLED = os.getenv('BACKUP_ENABLED', 'false').lower() == 'true'
    BACKUP_INTERVAL = int(os.getenv('BACKUP_INTERVAL', '3600'))
    BACKUP_LOCATION = os.getenv('BACKUP_LOCATION', 'backups/')
    
    # === DEVELOPMENT SETTINGS ===
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'true').lower() == 'true'
    HOT_RELOAD = os.getenv('HOT_RELOAD', 'true').lower() == 'true'
    PROFILING_ENABLED = os.getenv('PROFILING_ENABLED', 'false').lower() == 'true'
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        errors = []
        
        # Check required directories exist or can be created
        required_dirs = [
            cls.UPLOAD_FOLDER,
            cls.TEMPLATES_FOLDER,
            cls.REPORTS_FOLDER
        ]
        
        for dir_path in required_dirs:
            try:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create directory {dir_path}: {e}")
        
        # Validate numeric ranges
        if cls.MAX_CONTENT_LENGTH < 1024 or cls.MAX_CONTENT_LENGTH > 100 * 1024 * 1024:
            errors.append("MAX_CONTENT_LENGTH must be between 1KB and 100MB")
        
        if cls.OPENAI_TIMEOUT < 1 or cls.OPENAI_TIMEOUT > 300:
            errors.append("OPENAI_TIMEOUT must be between 1 and 300 seconds")
        
        if cls.LLM_TEMPERATURE < 0.0 or cls.LLM_TEMPERATURE > 2.0:
            errors.append("LLM_TEMPERATURE must be between 0.0 and 2.0")
        
        if cls.PORT < 1024 or cls.PORT > 65535:
            errors.append("FLASK_PORT must be between 1024 and 65535")
        
        # Validate LLM provider configuration
        if cls.LLM_PROVIDER != 'openai':
            errors.append("LLM_PROVIDER must be 'openai' - only OpenAI is supported")
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required")
        
        return errors
    
    @classmethod
    def get_summary(cls):
        """Get configuration summary for logging"""
        summary = {
            'flask_host': cls.HOST,
            'flask_port': cls.PORT,
            'debug': cls.DEBUG,
            'llm_provider': cls.LLM_PROVIDER,
            'upload_folder': cls.UPLOAD_FOLDER,
            'max_file_size': f"{cls.MAX_CONTENT_LENGTH // (1024*1024)}MB",
            'allowed_extensions': cls.ALLOWED_EXTENSIONS,
            'log_level': cls.LOG_LEVEL
        }
        
        # Add OpenAI-specific info
        summary.update({
            'openai_model': cls.OPENAI_MODEL,
            'openai_api_key': 'configured' if cls.OPENAI_API_KEY else 'not configured'
        })
        
        return summary

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENV = 'development'
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    ENV = 'production'
    LOG_LEVEL = 'WARNING'
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')  # Must be set in production
    HOST = os.getenv('FLASK_HOST', '127.0.0.1')  # Respect environment variable
    
    @classmethod
    def validate_config(cls):
        """Additional validation for production"""
        errors = super().validate_config()
        
        if cls.SECRET_KEY == 'dev-key-change-in-production':
            errors.append("SECRET_KEY must be changed in production")
        
        if cls.DEBUG:
            errors.append("DEBUG must be False in production")
        
        return errors

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    ENV = 'testing'
    UPLOAD_FOLDER = 'test_uploads'
    TEMPLATES_FOLDER = 'test_templates'
    REPORTS_FOLDER = 'test_reports'

# Configuration factory
def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig

# Default configuration instance
config = get_config() 