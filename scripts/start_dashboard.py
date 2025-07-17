#!/usr/bin/env python3
"""
Enhanced startup script for Contract Analyzer Dashboard
Uses configuration system and improved error handling
"""

import sys
import os
import time
import threading
import webbrowser
import logging
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import configuration and dashboard
from src.config import config
from src.dashboard_server import DashboardServer

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = {
        'flask': 'flask',
        'python-docx': 'docx',
        'requests': 'requests',
        'werkzeug': 'werkzeug',
        'python-dotenv': 'dotenv',
        'openai': 'openai'
    }
    
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            logger.debug(f"✓ {package_name} found")
        except ImportError:
            missing_packages.append(package_name)
            logger.error(f"✗ {package_name} not found")
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("✓ All dependencies found")
    return True

def check_openai_connection():
    """Check if OpenAI API key is configured"""
    try:
        if not config.OPENAI_API_KEY:
            print("✗ OpenAI API key not configured")
            print("Please set OPENAI_API_KEY in your .env file")
            return False
        
        # Test API key by making a simple request
        import openai
        client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        
        # Try to list models to verify API key works
        models = client.models.list()
        print(f"✓ OpenAI API connection successful - Model '{config.OPENAI_MODEL}' will be used")
        return True
        
    except Exception as e:
        print(f"✗ OpenAI API connection failed: {e}")
        print("Please check your OPENAI_API_KEY in the .env file")
        return False

def validate_environment():
    """Validate the environment and configuration"""
    print("\n🔧 Validating environment...")
    
    # Validate configuration
    config_errors = config.validate_config()
    if config_errors:
        print("✗ Configuration validation failed:")
        for error in config_errors:
            print(f"  - {error}")
        return False
    
    print("✓ Configuration valid")
    
    # Check disk space
    try:
        import shutil
        usage = shutil.disk_usage(config.BASE_DIR)
        free_gb = usage.free / (1024**3)
        
        if free_gb < 1:
            print(f"✗ Low disk space: {free_gb:.1f}GB available")
            return False
        
        print(f"✓ Disk space: {free_gb:.1f}GB available")
    except Exception as e:
        print(f"⚠️  Could not check disk space: {e}")
    
    # Check write permissions
    try:
        test_file = Path(config.UPLOAD_FOLDER) / 'test_write.tmp'
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("test")
        test_file.unlink()
        print("✓ Write permissions OK")
    except Exception as e:
        print(f"✗ Write permission check failed: {e}")
        return False
    
    return True

def open_browser_delayed(url, delay=3):
    """Open browser after a delay"""
    def open_browser():
        time.sleep(delay)
        try:
            webbrowser.open(url)
            logger.info(f"Browser opened to {url}")
        except Exception as e:
            logger.error(f"Failed to open browser: {e}")
    
    threading.Thread(target=open_browser, daemon=True).start()

def print_startup_banner():
    """Print startup banner with configuration info"""
    banner = f"""
{'=' * 60}
🚀 CONTRACT ANALYZER DASHBOARD
{'=' * 60}

Configuration:
  Host: {config.HOST}
  Port: {config.PORT}
  Debug: {config.DEBUG}
  Environment: {config.ENV}
  
  Upload Folder: {config.UPLOAD_FOLDER}
  Templates Folder: {config.TEMPLATES_FOLDER}
  Reports Folder: {config.REPORTS_FOLDER}
  
  Max File Size: {config.MAX_CONTENT_LENGTH // (1024*1024)}MB
  Allowed Extensions: {', '.join(config.ALLOWED_EXTENSIONS)}
  
  OpenAI Model: {config.OPENAI_MODEL}
  OpenAI API Key: {'configured' if config.OPENAI_API_KEY else 'not configured'}
  
  Log Level: {config.LOG_LEVEL}
  Log File: {config.LOG_FILE}
{'=' * 60}
"""
    print(banner)

def print_feature_summary():
    """Print feature summary"""
    features = """
📋 Available Features:
   • Upload and analyze contracts
   • Manage templates
   • View analysis reports
   • Monitor compliance metrics
   • Configure settings
   • Enhanced security validation
   • Comprehensive error handling
   • Audit logging

🔧 Controls:
   • Press Ctrl+C to stop the server
   • Visit /api/health for system status
   • Check security_audit.log for security events
"""
    print(features)

def main():
    """Main function to start the dashboard"""
    try:
        print_startup_banner()
        
        # Check dependencies
        print("\n📦 Checking dependencies...")
        if not check_dependencies():
            sys.exit(1)
        
        # Validate environment
        if not validate_environment():
            sys.exit(1)
        
        # Check OpenAI connection
        print("\n🤖 Checking OpenAI connection...")
        openai_available = check_openai_connection()
        if not openai_available:
            print("⚠️  Warning: OpenAI not available. AI analysis will use fallback methods.")
            print("   Please configure your OpenAI API key in the .env file")
        
        # Print feature summary
        print_feature_summary()
        
        # URL for the dashboard
        url = f"http://{config.HOST}:{config.PORT}"
        
        print(f"\n🌐 Starting dashboard server...")
        print(f"   URL: {url}")
        
        # Create and configure server
        server = DashboardServer()
        
        # Start browser in background if not in debug mode
        if not config.DEBUG:
            print("✓ Browser will open automatically")
            open_browser_delayed(url, 3)
        
        print("\n✓ Dashboard starting...")
        print(f"✓ Security features enabled")
        print(f"✓ Configuration validated")
        print(f"✓ Audit logging active")
        
        # Log startup
        logger.info("Dashboard startup initiated")
        logger.info(f"Configuration: {config.get_summary()}")
        
        # Start the Flask server
        server.run()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        logger.error(f"Server startup failed: {e}")
        
        # Print troubleshooting tips
        print("\n🔧 Troubleshooting:")
        print("1. Check if port is already in use")
        print("2. Verify all dependencies are installed")
        print("3. Check file permissions")
        print("4. Review configuration settings")
        print("5. Check log files for detailed errors")
        
        sys.exit(1)

if __name__ == '__main__':
    main() 