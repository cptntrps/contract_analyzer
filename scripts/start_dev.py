#!/usr/bin/env python3
"""
Development Server Startup Script

Starts the Contract Analyzer application in development mode with
hot reloading and debugging enabled.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set development environment
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('DEBUG', 'true')

try:
    from app import create_app
    from app.config.settings import get_config
    
    def main():
        """Main entry point for development server"""
        config = get_config('development')
        
        # Validate configuration
        config_errors = config.validate_config()
        if config_errors:
            print("❌ Configuration validation failed:")
            for error in config_errors:
                print(f"  - {error}")
            sys.exit(1)
        
        # Create application
        app = create_app('development')
        
        print("🚀 CONTRACT ANALYZER - DEVELOPMENT SERVER")
        print("=" * 50)
        print(f"Environment: {config.ENV}")
        print(f"Debug: {config.DEBUG}")
        print(f"Host: {config.HOST}")
        print(f"Port: {config.PORT}")
        print(f"Log Level: {config.LOG_LEVEL}")
        print("=" * 50)
        print()
        print("📝 Available endpoints:")
        print("  - Dashboard: http://localhost:5000/")
        print("  - Health Check: http://localhost:5000/api/health")
        print("  - API Documentation: http://localhost:5000/api/")
        print()
        print("🔧 Controls:")
        print("  - Press Ctrl+C to stop the server")
        print("  - Files will auto-reload on changes")
        print()
        
        try:
            # Run development server
            app.run(
                host=config.HOST,
                port=config.PORT,
                debug=config.DEBUG,
                use_reloader=True,
                use_debugger=True
            )
        except KeyboardInterrupt:
            print("\n👋 Development server stopped")
        except Exception as e:
            print(f"\n❌ Server error: {e}")
            sys.exit(1)
    
    if __name__ == '__main__':
        main()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    print("and that all dependencies are installed:")
    print("  pip install -r config/requirements.txt")
    sys.exit(1)