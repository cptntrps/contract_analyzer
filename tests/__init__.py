"""
Contract Analyzer Test Suite
============================

Comprehensive testing suite for the Contract Analyzer application.

Test Structure:
- unit/: Unit tests for individual components
- integration/: Integration tests for component interactions
- e2e/: End-to-end tests for complete workflows
- fixtures/: Test data and mock objects

Usage:
    # Run all tests
    python -m pytest tests/
    
    # Run specific test category
    python -m pytest tests/unit/
    python -m pytest tests/integration/
    python -m pytest tests/e2e/
    
    # Run with coverage
    python -m pytest tests/ --cov=. --cov-report=html
    
    # Run with verbose output
    python -m pytest tests/ -v
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test configuration
TEST_DATA_DIR = Path(__file__).parent / "fixtures"
TEST_UPLOAD_DIR = Path(tempfile.mkdtemp())
TEST_REPORTS_DIR = Path(tempfile.mkdtemp())
TEST_TEMPLATES_DIR = Path(tempfile.mkdtemp())

def setup_test_environment():
    """Setup test environment with clean directories"""
    for dir_path in [TEST_UPLOAD_DIR, TEST_REPORTS_DIR, TEST_TEMPLATES_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)

def cleanup_test_environment():
    """Clean up test environment"""
    for dir_path in [TEST_UPLOAD_DIR, TEST_REPORTS_DIR, TEST_TEMPLATES_DIR]:
        if dir_path.exists():
            shutil.rmtree(dir_path)

# Setup test environment on import
setup_test_environment()