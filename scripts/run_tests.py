#!/usr/bin/env python3
"""
Test runner for Contract Analyzer application
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_tests(test_type='all', verbose=False, coverage=False, parallel=False):
    """Run tests with specified options"""
    
    # Base pytest command
    cmd = ['python', '-m', 'pytest']
    
    # Add test directory based on type
    if test_type == 'unit':
        cmd.append('tests/unit/')
    elif test_type == 'integration':
        cmd.append('tests/integration/')
    elif test_type == 'e2e':
        cmd.append('tests/e2e/')
    elif test_type == 'all':
        cmd.append('tests/')
    else:
        print(f"Unknown test type: {test_type}")
        return False
    
    # Add verbose flag
    if verbose:
        cmd.append('-v')
    
    # Add coverage options
    if coverage:
        cmd.extend([
            '--cov=src',
            '--cov-report=html:output/coverage',
            '--cov-report=term-missing',
            '--cov-config=config/.coveragerc'
        ])
    
    # Add parallel execution
    if parallel:
        cmd.extend(['-n', 'auto'])
    
    # Add other useful options
    cmd.extend([
        '--tb=short',  # Short traceback format
        '--strict-markers',  # Strict marker checking
        '--disable-warnings'  # Disable warnings
    ])
    
    print(f"Running command: {' '.join(cmd)}")
    print("=" * 50)
    
    try:
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        return False
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

def install_test_dependencies():
    """Install required test dependencies"""
    
    dependencies = [
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0',
        'pytest-mock>=3.10.0',
        'pytest-xdist>=3.0.0',  # For parallel test execution
        'pytest-html>=3.1.0',   # For HTML test reports
        'pytest-json-report>=1.5.0'  # For JSON test reports
    ]
    
    print("Installing test dependencies...")
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                         check=True, capture_output=True)
            print(f"✓ Installed {dep}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {dep}: {e}")
            return False
    
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    
    required_modules = [
        'pytest',
        'pytest_cov',
        'pytest_mock',
        'xdist',  # pytest-xdist imports as 'xdist'
        'unittest.mock'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        return False
    
    return True

def generate_test_report():
    """Generate comprehensive test report"""
    
    print("Generating comprehensive test report...")
    
    # Run tests with HTML and JSON reports
    cmd = [
        'python', '-m', 'pytest', 'tests/',
        '--cov=src',
        '--cov-report=html:output/coverage',
        '--cov-report=term-missing',
        '--html=output/test-results/test_report.html',
        '--json-report',
        '--json-report-file=output/test-results/test_report.json',
        '--tb=short',
        '--disable-warnings'
    ]
    
    # Create output directories
    output_dir = project_root / 'output'
    output_dir.mkdir(exist_ok=True)
    (output_dir / 'test-results').mkdir(exist_ok=True)
    (output_dir / 'coverage').mkdir(exist_ok=True)
    
    try:
        result = subprocess.run(cmd, cwd=project_root)
        
        if result.returncode == 0:
            print("\n✓ Test report generated successfully!")
            print(f"HTML Report: {output_dir / 'test-results' / 'test_report.html'}")
            print(f"Coverage Report: {output_dir / 'coverage' / 'index.html'}")
            print(f"JSON Report: {output_dir / 'test-results' / 'test_report.json'}")
        else:
            print("\n✗ Test report generation failed")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error generating test report: {e}")
        return False

def run_specific_test(test_path):
    """Run a specific test file or function"""
    
    cmd = [
        'python', '-m', 'pytest',
        test_path,
        '-v',
        '--tb=short',
        '--disable-warnings'
    ]
    
    try:
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running specific test: {e}")
        return False

def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description='Test runner for Contract Analyzer application'
    )
    
    parser.add_argument(
        'test_type',
        choices=['unit', 'integration', 'e2e', 'all'],
        default='all',
        nargs='?',
        help='Type of tests to run (default: all)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '-c', '--coverage',
        action='store_true',
        help='Generate coverage report'
    )
    
    parser.add_argument(
        '-p', '--parallel',
        action='store_true',
        help='Run tests in parallel'
    )
    
    parser.add_argument(
        '--install-deps',
        action='store_true',
        help='Install test dependencies'
    )
    
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='Check if dependencies are installed'
    )
    
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate comprehensive test report'
    )
    
    parser.add_argument(
        '--test',
        type=str,
        help='Run specific test file or function'
    )
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.install_deps:
        success = install_test_dependencies()
        sys.exit(0 if success else 1)
    
    if args.check_deps:
        success = check_dependencies()
        if success:
            print("✓ All dependencies are installed")
        sys.exit(0 if success else 1)
    
    if args.report:
        success = generate_test_report()
        sys.exit(0 if success else 1)
    
    if args.test:
        success = run_specific_test(args.test)
        sys.exit(0 if success else 1)
    
    # Check dependencies before running tests
    if not check_dependencies():
        print("Some dependencies are missing. Run with --install-deps to install them.")
        sys.exit(1)
    
    # Run tests
    success = run_tests(
        test_type=args.test_type,
        verbose=args.verbose,
        coverage=args.coverage,
        parallel=args.parallel
    )
    
    if success:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed!")
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()