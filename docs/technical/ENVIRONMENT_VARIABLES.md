# Environment Variables Documentation

This document explains all environment variables used in the Contract Analyzer application. These variables can be set in a `.env` file in the project root or as system environment variables.

## Table of Contents

1. [Flask Configuration](#flask-configuration)
2. [Directory Paths](#directory-paths)
3. [File Upload Settings](#file-upload-settings)
4. [OpenAI Configuration](#openai-configuration)
5. [LLM Parameters](#llm-parameters)
6. [Security Settings](#security-settings)
7. [Logging Configuration](#logging-configuration)
8. [Analysis Settings](#analysis-settings)
9. [Performance Settings](#performance-settings)
10. [Monitoring](#monitoring)
11. [Dashboard Settings](#dashboard-settings)
12. [External Services](#external-services)
13. [Development Settings](#development-settings)
14. [Example .env File](#example-env-file)

---

## Flask Configuration

### FLASK_SECRET_KEY
- **Description**: Secret key for Flask sessions and CSRF protection
- **Default**: `dev-key-change-in-production`
- **Production**: **MUST** be set to a secure random string
- **Example**: `FLASK_SECRET_KEY=your-super-secure-random-key-here`

### FLASK_ENV
- **Description**: Environment mode for Flask application
- **Default**: `development`
- **Options**: `development`, `production`, `testing`
- **Example**: `FLASK_ENV=production`

### FLASK_DEBUG
- **Description**: Enable Flask debug mode
- **Default**: `true`
- **Options**: `true`, `false`
- **Example**: `FLASK_DEBUG=false`

### FLASK_HOST
- **Description**: Host address for the Flask application
- **Default**: `0.0.0.0` (all interfaces)
- **Production**: Consider `127.0.0.1` for security
- **Example**: `FLASK_HOST=127.0.0.1`

### FLASK_PORT
- **Description**: Port number for the Flask application
- **Default**: `5000`
- **Range**: 1024-65535
- **Example**: `FLASK_PORT=8080`

---

## Directory Paths

### UPLOAD_FOLDER
- **Description**: Directory for uploaded contract files
- **Default**: `uploads`
- **Example**: `UPLOAD_FOLDER=contract_uploads`

### TEMPLATES_FOLDER
- **Description**: Directory for contract templates
- **Default**: `contract_templates`
- **Example**: `TEMPLATES_FOLDER=templates`

### REPORTS_FOLDER
- **Description**: Directory for generated analysis reports
- **Default**: `reports`
- **Example**: `REPORTS_FOLDER=analysis_reports`

### STATIC_FOLDER
- **Description**: Directory for static web assets
- **Default**: `static`
- **Example**: `STATIC_FOLDER=web_assets`

### TEMPLATE_FOLDER
- **Description**: Directory for HTML templates
- **Default**: `templates`
- **Example**: `TEMPLATE_FOLDER=html_templates`

---

## File Upload Settings

### MAX_CONTENT_LENGTH
- **Description**: Maximum file upload size in bytes
- **Default**: `16777216` (16MB)
- **Range**: 1KB - 100MB
- **Example**: `MAX_CONTENT_LENGTH=33554432` (32MB)

### ALLOWED_EXTENSIONS
- **Description**: Comma-separated list of allowed file extensions
- **Default**: `docx`
- **Example**: `ALLOWED_EXTENSIONS=docx,pdf,doc`

### MAX_FILENAME_LENGTH
- **Description**: Maximum allowed filename length
- **Default**: `255`
- **Example**: `MAX_FILENAME_LENGTH=200`

---

## OpenAI Configuration

### LLM_PROVIDER
- **Description**: LLM provider to use for analysis
- **Default**: `openai`
- **Options**: `openai` (only OpenAI is currently supported)
- **Example**: `LLM_PROVIDER=openai`

### OPENAI_API_KEY
- **Description**: OpenAI API key for authentication
- **Default**: None (required)
- **Example**: `OPENAI_API_KEY=sk-proj-abcdef123456...`
- **Note**: **Required** - obtain from https://platform.openai.com/api-keys

### OPENAI_MODEL
- **Description**: OpenAI model to use for analysis
- **Default**: `gpt-4o`
- **Examples**: `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`
- **Example**: `OPENAI_MODEL=gpt-4o-mini`

### OPENAI_TIMEOUT
- **Description**: Timeout for OpenAI API requests in seconds
- **Default**: `30`
- **Range**: 1-300
- **Example**: `OPENAI_TIMEOUT=60`

### OPENAI_MAX_RETRIES
- **Description**: Maximum number of retry attempts for failed requests
- **Default**: `3`
- **Example**: `OPENAI_MAX_RETRIES=5`

### OPENAI_RETRY_DELAY
- **Description**: Delay between retry attempts in seconds
- **Default**: `2`
- **Example**: `OPENAI_RETRY_DELAY=5`

### OPENAI_BASE_URL
- **Description**: OpenAI API base URL (for custom endpoints)
- **Default**: `https://api.openai.com/v1`
- **Example**: `OPENAI_BASE_URL=https://api.openai.com/v1`

---

## LLM Parameters

### LLM_TEMPERATURE
- **Description**: Controls randomness in LLM responses (0.0 = deterministic, 2.0 = very random)
- **Default**: `0.1`
- **Range**: 0.0-2.0
- **Example**: `LLM_TEMPERATURE=0.3`

### LLM_TOP_P
- **Description**: Controls diversity of LLM responses (nucleus sampling)
- **Default**: `0.9`
- **Range**: 0.0-1.0
- **Example**: `LLM_TOP_P=0.85`

### LLM_MAX_TOKENS
- **Description**: Maximum number of tokens in LLM responses
- **Default**: `1024`
- **Example**: `LLM_MAX_TOKENS=2048`

---

## Security Settings

### SECURE_FILENAME_ENABLED
- **Description**: Enable secure filename sanitization
- **Default**: `true`
- **Options**: `true`, `false`
- **Example**: `SECURE_FILENAME_ENABLED=true`

### PATH_TRAVERSAL_PROTECTION
- **Description**: Enable protection against path traversal attacks
- **Default**: `true`
- **Options**: `true`, `false`
- **Example**: `PATH_TRAVERSAL_PROTECTION=true`

### FILE_VALIDATION_ENABLED
- **Description**: Enable file content validation
- **Default**: `true`
- **Options**: `true`, `false`
- **Example**: `FILE_VALIDATION_ENABLED=true`

### CONTENT_TYPE_VALIDATION
- **Description**: Enable MIME type validation for uploads
- **Default**: `true`
- **Options**: `true`, `false`
- **Example**: `CONTENT_TYPE_VALIDATION=true`

---

## Logging Configuration

### LOG_LEVEL
- **Description**: Logging level for the application
- **Default**: `INFO`
- **Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Example**: `LOG_LEVEL=DEBUG`

### LOG_FILE
- **Description**: Path to the log file
- **Default**: `dashboard.log`
- **Example**: `LOG_FILE=logs/contract_analyzer.log`

### LOG_FORMAT
- **Description**: Format string for log messages
- **Default**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Example**: `LOG_FORMAT=%(asctime)s [%(levelname)s] %(message)s`

---

## Analysis Settings

### SIMILARITY_THRESHOLD
- **Description**: Threshold for document similarity comparison
- **Default**: `0.5`
- **Range**: 0.0-1.0
- **Example**: `SIMILARITY_THRESHOLD=0.7`

### SIGNIFICANT_CHANGES_THRESHOLD
- **Description**: Minimum number of changes to consider significant
- **Default**: `10`
- **Example**: `SIGNIFICANT_CHANGES_THRESHOLD=15`

### ANALYSIS_TIMEOUT
- **Description**: Maximum time for analysis operations in seconds
- **Default**: `300` (5 minutes)
- **Example**: `ANALYSIS_TIMEOUT=600`

### BATCH_SIZE
- **Description**: Number of items to process in each batch
- **Default**: `10`
- **Example**: `BATCH_SIZE=20`

---

## Performance Settings

### CACHE_TIMEOUT
- **Description**: Cache timeout in seconds
- **Default**: `3600` (1 hour)
- **Example**: `CACHE_TIMEOUT=7200`

### REQUEST_TIMEOUT
- **Description**: Request timeout in seconds
- **Default**: `30`
- **Example**: `REQUEST_TIMEOUT=45`

### CONNECTION_POOL_SIZE
- **Description**: Size of connection pool for external services
- **Default**: `10`
- **Example**: `CONNECTION_POOL_SIZE=20`

---

## Monitoring

### HEALTH_CHECK_INTERVAL
- **Description**: Health check interval in seconds
- **Default**: `30`
- **Example**: `HEALTH_CHECK_INTERVAL=60`

### METRICS_ENABLED
- **Description**: Enable application metrics collection
- **Default**: `true`
- **Options**: `true`, `false`
- **Example**: `METRICS_ENABLED=false`

### MONITORING_ENDPOINT
- **Description**: Health check endpoint path
- **Default**: `/api/health`
- **Example**: `MONITORING_ENDPOINT=/health`

---

## Dashboard Settings

### DASHBOARD_TITLE
- **Description**: Title displayed in the dashboard
- **Default**: `Contract Analyzer Dashboard`
- **Example**: `DASHBOARD_TITLE=Legal Contract Analysis Platform`

### DASHBOARD_THEME
- **Description**: Dashboard theme mode
- **Default**: `auto`
- **Options**: `auto`, `light`, `dark`
- **Example**: `DASHBOARD_THEME=dark`

### AUTO_REFRESH_INTERVAL
- **Description**: Auto-refresh interval for dashboard in milliseconds
- **Default**: `30000` (30 seconds)
- **Example**: `AUTO_REFRESH_INTERVAL=60000`

### PAGINATION_SIZE
- **Description**: Number of items per page in listings
- **Default**: `20`
- **Example**: `PAGINATION_SIZE=50`

---

## External Services

### BACKUP_ENABLED
- **Description**: Enable automatic backups
- **Default**: `false`
- **Options**: `true`, `false`
- **Example**: `BACKUP_ENABLED=true`

### BACKUP_INTERVAL
- **Description**: Backup interval in seconds
- **Default**: `3600` (1 hour)
- **Example**: `BACKUP_INTERVAL=7200`

### BACKUP_LOCATION
- **Description**: Directory for backup files
- **Default**: `backups/`
- **Example**: `BACKUP_LOCATION=/var/backups/contract_analyzer/`

---

## Development Settings

### DEBUG_MODE
- **Description**: Enable debug mode features
- **Default**: `true`
- **Options**: `true`, `false`
- **Example**: `DEBUG_MODE=false`

### HOT_RELOAD
- **Description**: Enable hot reload for development
- **Default**: `true`
- **Options**: `true`, `false`
- **Example**: `HOT_RELOAD=false`

### PROFILING_ENABLED
- **Description**: Enable performance profiling
- **Default**: `false`
- **Options**: `true`, `false`
- **Example**: `PROFILING_ENABLED=true`

---

## Example .env File

```env
# Flask Configuration
FLASK_SECRET_KEY=your-super-secure-random-key-here
FLASK_ENV=production
FLASK_DEBUG=false
FLASK_HOST=127.0.0.1
FLASK_PORT=5000

# Directory Paths
UPLOAD_FOLDER=uploads
TEMPLATES_FOLDER=contract_templates
REPORTS_FOLDER=reports
STATIC_FOLDER=static
TEMPLATE_FOLDER=templates

# File Upload Settings
MAX_CONTENT_LENGTH=16777216
ALLOWED_EXTENSIONS=docx,pdf,doc
MAX_FILENAME_LENGTH=255

# LLM Provider Configuration
LLM_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-api-key-here
OPENAI_MODEL=gpt-4o
OPENAI_TIMEOUT=30
OPENAI_MAX_RETRIES=3
OPENAI_RETRY_DELAY=2
OPENAI_BASE_URL=https://api.openai.com/v1

# LLM Parameters
LLM_TEMPERATURE=0.1
LLM_TOP_P=0.9
LLM_MAX_TOKENS=1024

# Security Settings
SECURE_FILENAME_ENABLED=true
PATH_TRAVERSAL_PROTECTION=true
FILE_VALIDATION_ENABLED=true
CONTENT_TYPE_VALIDATION=true

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=dashboard.log
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# Analysis Settings
SIMILARITY_THRESHOLD=0.5
SIGNIFICANT_CHANGES_THRESHOLD=10
ANALYSIS_TIMEOUT=300
BATCH_SIZE=10

# Performance Settings
CACHE_TIMEOUT=3600
REQUEST_TIMEOUT=30
CONNECTION_POOL_SIZE=10

# Monitoring
HEALTH_CHECK_INTERVAL=30
METRICS_ENABLED=true
MONITORING_ENDPOINT=/api/health

# Dashboard Settings
DASHBOARD_TITLE=Contract Analyzer Dashboard
DASHBOARD_THEME=auto
AUTO_REFRESH_INTERVAL=30000
PAGINATION_SIZE=20

# External Services
BACKUP_ENABLED=false
BACKUP_INTERVAL=3600
BACKUP_LOCATION=backups/

# Development Settings
DEBUG_MODE=true
HOT_RELOAD=true
PROFILING_ENABLED=false
```

---

## Notes

1. **Production Deployment**: Always set `FLASK_SECRET_KEY` to a secure random string in production
2. **Security**: Review security settings and adjust according to your deployment requirements
3. **Performance**: Adjust timeout and batch size settings based on your system capabilities
4. **Monitoring**: Enable metrics and monitoring in production environments
5. **Backups**: Consider enabling backups for production deployments

For more information, refer to the `config.py` file in the project root. 