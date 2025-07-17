#!/usr/bin/env python3
"""
Simple test runner to verify testing setup
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Run a simple test to verify setup"""
    
    print("🧪 Contract Analyzer Test Suite")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not (project_root / 'tests').exists():
        print("❌ Tests directory not found!")
        return False
    
    # Check if pytest is available
    try:
        result = subprocess.run([sys.executable, '-m', 'pytest', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Pytest available: {result.stdout.strip()}")
        else:
            print("❌ Pytest not available")
            return False
    except Exception as e:
        print(f"❌ Error checking pytest: {e}")
        return False
    
    # Check if test directories exist
    test_dirs = ['unit', 'integration', 'e2e', 'fixtures']
    for test_dir in test_dirs:
        test_path = project_root / 'tests' / test_dir
        if test_path.exists():
            print(f"✅ Test directory exists: {test_dir}")
        else:
            print(f"❌ Test directory missing: {test_dir}")
    
    # Run a basic test discovery
    print("\n🔍 Discovering tests...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            '--collect-only', 
            '--quiet', 
            'tests/'
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            test_count = result.stdout.count('::')
            print(f"✅ Found {test_count} tests")
            
            # Show some examples
            lines = result.stdout.split('\n')
            examples = [line for line in lines if '::' in line][:5]
            if examples:
                print("📋 Example tests:")
                for example in examples:
                    print(f"   • {example.strip()}")
        else:
            print("❌ Test discovery failed")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error discovering tests: {e}")
        return False
    
    # Try to run a simple test
    print("\n🏃 Running basic tests...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            'tests/unit/test_analyzer.py::TestContractAnalyzer::test_init',
            '-v'
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ Basic test passed!")
        else:
            print("❌ Basic test failed")
            print(f"Output: {result.stdout}")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running basic test: {e}")
        return False
    
    print("\n🎉 Test setup verification complete!")
    print("\nNext steps:")
    print("1. Install test dependencies: python -m pip install -r test-requirements.txt")
    print("2. Run all tests: python run_tests.py")
    print("3. Run specific test types: python run_tests.py unit")
    print("4. Generate coverage report: python run_tests.py --coverage")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)