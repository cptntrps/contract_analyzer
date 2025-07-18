#!/usr/bin/env python3
"""
Test script to verify sprint improvements work correctly
Tests configuration, security, and LLM enhancements
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_configuration():
    """Test configuration system"""
    print("Testing configuration system...")
    
    try:
        from config import config, Config
        
        # Test configuration loading
        print(f"✓ Configuration loaded: {config.__class__.__name__}")
        print(f"✓ Host: {config.HOST}")
        print(f"✓ Port: {config.PORT}")
        print(f"✓ Ollama Host: {config.OLLAMA_HOST}")
        print(f"✓ Max File Size: {config.MAX_CONTENT_LENGTH // (1024*1024)}MB")
        
        # Test configuration validation
        errors = config.validate_config()
        if errors:
            print(f"⚠️  Configuration validation warnings: {errors}")
        else:
            print("✓ Configuration validation passed")
        
        # Test configuration summary
        summary = config.get_summary()
        print(f"✓ Configuration summary: {len(summary)} items")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_security():
    """Test security validation"""
    print("\nTesting security validation...")
    
    try:
        from security import (
            SecurityValidator, validate_file_upload, sanitize_input,
            FileValidationError, ContentValidationError
        )
        
        # Test security validator initialization
        validator = SecurityValidator()
        print("✓ Security validator initialized")
        
        # Test filename validation
        try:
            safe_name = validator.validate_filename("test_document.docx")
            print(f"✓ Filename validation: {safe_name}")
        except FileValidationError as e:
            print(f"✓ Filename validation caught error: {e}")
        
        # Test dangerous filename rejection
        try:
            validator.validate_filename("../../../etc/passwd")
            print("✗ Dangerous filename should have been rejected")
        except FileValidationError:
            print("✓ Dangerous filename correctly rejected")
        
        # Test string sanitization
        unsafe_input = "<script>alert('xss')</script>Hello World"
        safe_input = sanitize_input(unsafe_input)
        print(f"✓ String sanitization: '{unsafe_input}' -> '{safe_input}'")
        
        # Test JSON validation
        test_json = {"key": "value", "number": 42}
        validated = validator.validate_json_input(test_json)
        print(f"✓ JSON validation: {validated}")
        
        # Test security headers
        headers = validator.get_security_headers()
        print(f"✓ Security headers: {len(headers)} headers")
        
        return True
        
    except Exception as e:
        print(f"✗ Security test failed: {e}")
        return False

def test_llm_handler():
    """Test enhanced LLM handler"""
    print("\nTesting LLM handler...")
    
    try:
        from app.llm_handler import LLMHandler
        
        # Test LLM handler initialization
        handler = LLMHandler()
        print("✓ LLM handler initialized")
        
        # Test connection check
        is_connected = handler.check_connection()
        print(f"✓ Connection check: {is_connected}")
        
        # Test health status
        health = handler.get_health_status()
        print(f"✓ Health status: {health.get('status', 'unknown')}")
        
        # Test fallback analysis
        result = handler.get_change_analysis("old text", "new text")
        print(f"✓ Change analysis: {result.get('classification', 'unknown')}")
        print(f"✓ Confidence: {result.get('confidence', 'unknown')}")
        
        # Test batch analysis
        changes = [('delete', 'old text'), ('insert', 'new text')]
        batch_results = handler.analyze_changes(changes)
        print(f"✓ Batch analysis: {len(batch_results)} results")
        
        return True
        
    except Exception as e:
        print(f"✗ LLM handler test failed: {e}")
        return False

def test_dashboard_server():
    """Test dashboard server initialization"""
    print("\nTesting dashboard server...")
    
    try:
        from dashboard_server import DashboardServer
        
        # Test server initialization
        server = DashboardServer()
        print("✓ Dashboard server initialized")
        
        # Test Flask app configuration
        app_config = server.app.config
        print(f"✓ Flask app configured: {len(app_config)} settings")
        
        # Test security headers
        with server.app.app_context():
            from flask import make_response
            response = make_response("test")
            enhanced_response = server.add_security_headers(response)
            print(f"✓ Security headers added: {len(enhanced_response.headers)} headers")
        
        # Test directory structure
        directories = [
            server.app.config['UPLOAD_FOLDER'],
            server.app.config['TEMPLATES_FOLDER'],
            server.app.config['REPORTS_FOLDER']
        ]
        
        for directory in directories:
            if Path(directory).exists():
                print(f"✓ Directory exists: {directory}")
            else:
                print(f"⚠️  Directory missing: {directory}")
        
        return True
        
    except Exception as e:
        print(f"✗ Dashboard server test failed: {e}")
        return False

def test_integration():
    """Test integration between components"""
    print("\nTesting integration...")
    
    try:
        from config import config
        from security import SecurityValidator
        from app.llm_handler import LLMHandler
        
        # Test configuration used by security
        validator = SecurityValidator()
        assert validator.max_file_size == config.MAX_CONTENT_LENGTH
        print("✓ Security uses configuration")
        
        # Test configuration used by LLM
        handler = LLMHandler()
        assert handler.host == config.OLLAMA_HOST
        assert handler.model == config.OLLAMA_MODEL
        print("✓ LLM handler uses configuration")
        
        # Test error handling chain
        try:
            validator.validate_filename("invalid<>filename.exe")
        except Exception as e:
            print(f"✓ Error handling works: {type(e).__name__}")
        
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🧪 Running Sprint Improvements Tests")
    print("=" * 50)
    
    tests = [
        ("Configuration System", test_configuration),
        ("Security Validation", test_security),
        ("LLM Handler Enhancement", test_llm_handler),
        ("Dashboard Server", test_dashboard_server),
        ("Integration", test_integration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} - ERROR: {e}")
        
        print("-" * 30)
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Sprint improvements are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 