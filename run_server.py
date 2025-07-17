#!/usr/bin/env python3
"""
Simple server runner for Contract Analyzer Dashboard
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from src.dashboard_server import DashboardServer

if __name__ == "__main__":
    print("🚀 Starting Contract Analyzer Dashboard...")
    server = DashboardServer()
    print("✅ Server initialized")
    print("🌐 Starting Flask server on http://localhost:5000")
    print("📋 Press Ctrl+C to stop")
    
    try:
        server.run(host='127.0.0.1', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()