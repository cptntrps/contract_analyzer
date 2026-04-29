#!/usr/bin/env python3
"""
Demo script to showcase the Contract Analyzer Dashboard
"""

import os
import time
import subprocess
import webbrowser
from pathlib import Path

def main():
    print("🎯 CONTRACT ANALYZER DASHBOARD DEMO")
    print("=" * 50)
    print()
    
    # Check system status
    print("📋 System Status Check:")
    print(f"✅ Templates: {len(list(Path('templates').glob('*.docx')))} found")
    print(f"✅ Test Contracts: {len(list(Path('test_contracts').glob('*.docx')))} found")
    
    reports_dir = Path('reports')
    if reports_dir.exists() and (reports_dir / 'analysis_summary.json').exists():
        print("✅ Analysis Data: Available")
    else:
        print("⚠️  Analysis Data: Will use sample data")
    
    print()
    print("🚀 Dashboard Features:")
    print("   📊 Real-time compliance metrics")
    print("   📝 Contract upload and analysis")
    print("   📋 Template management")
    print("   📈 Downloadable Word reports with track changes")
    print("   ⚙️  Configurable settings")
    print()
    
    print("🎨 UI Features:")
    print("   🎯 Modern responsive design")
    print("   🌙 Dark mode support")
    print("   📱 Mobile-friendly interface")
    print("   🎭 Professional styling")
    print()
    
    # Offer demo options
    print("Demo Options:")
    print("1. 🌐 Start Web Dashboard (Full features)")
    print("2. 📄 Open Static Dashboard (View only)")
    print("3. ❌ Exit")
    print()
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice == "1":
        print("\n🚀 Starting web dashboard...")
        print("📊 Dashboard will open at: http://localhost:5000")
        print("⏹️  Press Ctrl+C to stop the server")
        print()
        
        try:
            # Start the Flask server
            from dashboard_server import app
            
            # Open browser after a delay
            import threading
            def open_browser():
                time.sleep(2)
                webbrowser.open('http://localhost:5000')
            
            threading.Thread(target=open_browser, daemon=True).start()
            app.run(host='0.0.0.0', port=5000, debug=False)
            
        except KeyboardInterrupt:
            print("\n👋 Dashboard stopped")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Tip: Make sure Flask is installed with 'pip install flask'")
    
    elif choice == "2":
        print("\n📄 Opening static dashboard...")
        dashboard_path = Path('dashboard.html').absolute()
        print(f"📂 File: {dashboard_path}")
        
        try:
            webbrowser.open(f'file://{dashboard_path}')
            print("✅ Dashboard opened in browser")
            print("ℹ️  Note: Static version has limited functionality")
        except Exception as e:
            print(f"❌ Could not open browser: {e}")
            print(f"💡 Manually open: {dashboard_path}")
    
    elif choice == "3":
        print("\n👋 Goodbye!")
    
    else:
        print("\n❌ Invalid choice")

if __name__ == "__main__":
    main()