#!/usr/bin/env python3
"""
Startup script for Contract Analyzer Dashboard
"""

import os
import sys
import webbrowser
import time
import threading
from pathlib import Path

def open_browser():
    """Open browser after server starts"""
    time.sleep(2)  # Wait for server to start
    webbrowser.open('http://localhost:5001')

def main():
    print("=" * 60)
    print("CONTRACT ANALYZER DASHBOARD")
    print("=" * 60)
    print()
    
    # Check if we have templates
    templates_dir = Path('templates')
    if not templates_dir.exists() or not list(templates_dir.glob('*.docx')):
        print("⚠️  WARNING: No templates found!")
        print("   Make sure you have .docx template files in the 'templates' directory")
        print()
    
    # Check if we have any analysis data
    reports_dir = Path('reports')
    if reports_dir.exists() and (reports_dir / 'analysis_summary.json').exists():
        print("✅ Found existing analysis data")
    else:
        print("ℹ️  No analysis data found - dashboard will show sample data")
        
    print()
    print("🚀 Starting dashboard server...")
    print("📊 Dashboard URL: http://localhost:5001")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    # Open browser in background
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start the Flask server
    try:
        from dashboard_server import app
        app.run(host='0.0.0.0', port=5001, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print("\n📝 You can still view the dashboard by opening 'dashboard.html' in your browser")

if __name__ == "__main__":
    main()