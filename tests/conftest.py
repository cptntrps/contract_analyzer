"""
Pytest configuration and fixtures for Contract Analyzer tests
"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import Mock, patch
import json

# Import test utilities
from tests import TEST_DATA_DIR, TEST_UPLOAD_DIR, TEST_REPORTS_DIR, TEST_TEMPLATES_DIR

# Import application modules
from src.config import config
from src.dashboard_server import DashboardServer
from src.analyzer import ContractAnalyzer
from src.llm_handler import LLMHandler
from src.llm_providers import OpenAIProvider
from src.enhanced_report_generator import EnhancedReportGenerator
from src.security import SecurityValidator
from src.user_config_manager import UserConfigManager

@pytest.fixture(scope="session")
def test_config():
    """Test configuration with safe defaults"""
    return {
        'UPLOAD_FOLDER': str(TEST_UPLOAD_DIR),
        'REPORTS_FOLDER': str(TEST_REPORTS_DIR),
        'TEMPLATES_FOLDER': str(TEST_TEMPLATES_DIR),
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
        'ALLOWED_EXTENSIONS': ['docx'],
        'DEBUG': True,
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'FLASK_HOST': '127.0.0.1',
        'FLASK_PORT': 5001,  # Different from production
        'LOG_LEVEL': 'DEBUG',
        'OPENAI_API_KEY': 'test-api-key',
        'OPENAI_MODEL': 'gpt-4o',
        'LLM_PROVIDER': 'openai',
        'LLM_TEMPERATURE': 0.1,
        'LLM_MAX_TOKENS': 2000,
        'LLM_TIMEOUT': 30
    }

@pytest.fixture
def mock_config(test_config):
    """Mock configuration for testing"""
    # Create a mock config object with the test config attributes
    mock_config_obj = Mock()
    for key, value in test_config.items():
        setattr(mock_config_obj, key.upper(), value)
    
    # Patch only the modules that actually import config
    with patch('src.dashboard_server.config', mock_config_obj), \
         patch('src.config.config', mock_config_obj), \
         patch('src.llm_handler.config', mock_config_obj), \
         patch('src.user_config_manager.config', mock_config_obj), \
         patch('src.security.config', mock_config_obj):
        yield mock_config_obj

@pytest.fixture
def sample_contract_text():
    """Sample contract text for testing"""
    return """
    CONSULTING AGREEMENT
    
    This Consulting Agreement ("Agreement") is entered into on January 1, 2025,
    between Acme Corporation ("Company") and John Smith ("Consultant").
    
    1. SCOPE OF WORK
    The Consultant agrees to provide software development services as described
    in the attached Statement of Work.
    
    2. COMPENSATION
    The Company will pay the Consultant $150 per hour for services rendered.
    Payment will be made within 30 days of invoice receipt.
    
    3. TERMINATION
    Either party may terminate this agreement with 30 days written notice.
    
    4. CONFIDENTIALITY
    The Consultant agrees to maintain confidentiality of all proprietary information.
    """

@pytest.fixture
def sample_template_text():
    """Sample template text for testing"""
    return """
    CONSULTING AGREEMENT
    
    This Consulting Agreement ("Agreement") is entered into on [DATE],
    between [COMPANY NAME] ("Company") and [CONSULTANT NAME] ("Consultant").
    
    1. SCOPE OF WORK
    The Consultant agrees to provide [SERVICE TYPE] services as described
    in the attached Statement of Work.
    
    2. COMPENSATION
    The Company will pay the Consultant $[HOURLY_RATE] per hour for services rendered.
    Payment will be made within [PAYMENT_TERMS] days of invoice receipt.
    
    3. TERMINATION
    Either party may terminate this agreement with [NOTICE_PERIOD] days written notice.
    
    4. CONFIDENTIALITY
    The Consultant agrees to maintain confidentiality of all proprietary information.
    """

@pytest.fixture
def sample_changes():
    """Sample changes for testing analysis"""
    return [
        ('delete', '[DATE]'),
        ('insert', 'January 1, 2025'),
        ('delete', '[COMPANY NAME]'),
        ('insert', 'Acme Corporation'),
        ('delete', '[CONSULTANT NAME]'),
        ('insert', 'John Smith'),
        ('delete', '[SERVICE TYPE]'),
        ('insert', 'software development'),
        ('delete', '$[HOURLY_RATE]'),
        ('insert', '$150'),
        ('delete', '[PAYMENT_TERMS]'),
        ('insert', '30'),
        ('delete', '[NOTICE_PERIOD]'),
        ('insert', '30')
    ]

@pytest.fixture
def sample_analysis_result():
    """Sample analysis result with multi-stakeholder data"""
    return {
        'explanation': 'Updated hourly rate from placeholder to $150',
        'category': 'FINANCIAL',
        'classification': 'SIGNIFICANT',
        'financial_impact': 'DIRECT',
        'required_reviews': ['FINANCE_APPROVAL', 'LEGAL_REVIEW'],
        'procurement_flags': ['rate_change', 'vendor_performance_impact'],
        'review_priority': 'high',
        'deleted_text': '$[HOURLY_RATE]',
        'inserted_text': '$150',
        'confidence': 'high'
    }

@pytest.fixture
def mock_llm_handler():
    """Mock LLM handler for testing"""
    handler = Mock(spec=LLMHandler)
    handler.get_change_analysis.return_value = {
        'explanation': 'Test analysis result',
        'classification': 'SIGNIFICANT',
        'category': 'FINANCIAL',
        'financial_impact': 'DIRECT',
        'required_reviews': ['FINANCE_APPROVAL'],
        'procurement_flags': ['test_flag'],
        'review_priority': 'high',
        'confidence': 'high'
    }
    handler.check_connection.return_value = True
    handler.get_current_model.return_value = 'test-model'
    handler.get_available_models.return_value = [
        {'name': 'test-model', 'description': 'Test model'}
    ]
    return handler


@pytest.fixture
def mock_openai_provider():
    """Mock OpenAI provider for testing"""
    provider = Mock(spec=OpenAIProvider)
    provider.check_connection.return_value = True
    provider.get_current_model.return_value = 'gpt-4o'
    provider.get_available_models.return_value = [
        {'name': 'gpt-4o', 'description': 'Test GPT-4o model', 'current': True, 'recommended': True}
    ]
    provider._generate_response.return_value = '{"explanation": "Test response"}'
    return provider

@pytest.fixture
def test_docx_file():
    """Create a test DOCX file"""
    from docx import Document
    
    doc = Document()
    doc.add_heading('Test Contract', 0)
    doc.add_paragraph('This is a test contract for testing purposes.')
    doc.add_paragraph('It contains sample text that can be analyzed.')
    
    test_file = TEST_DATA_DIR / 'test_contract.docx'
    test_file.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(test_file))
    
    yield test_file
    
    # Cleanup
    if test_file.exists():
        test_file.unlink()

@pytest.fixture
def test_template_file():
    """Create a test template DOCX file"""
    from docx import Document
    
    doc = Document()
    doc.add_heading('Test Template', 0)
    doc.add_paragraph('This is a test template for testing purposes.')
    doc.add_paragraph('It contains [PLACEHOLDER] text that should be replaced.')
    
    test_file = TEST_DATA_DIR / 'test_template.docx'
    test_file.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(test_file))
    
    yield test_file
    
    # Cleanup
    if test_file.exists():
        test_file.unlink()

@pytest.fixture
def analyzer():
    """Contract analyzer instance"""
    return ContractAnalyzer()

@pytest.fixture
def security_validator():
    """Security validator instance"""
    return SecurityValidator()

@pytest.fixture
def user_config_manager():
    """User config manager instance"""
    return UserConfigManager()

@pytest.fixture
def report_generator():
    """Enhanced report generator instance"""
    return EnhancedReportGenerator(reports_dir=str(TEST_REPORTS_DIR))

@pytest.fixture
def flask_app(mock_config):
    """Flask application instance for testing"""
    with patch('src.dashboard_server.config', mock_config):
        server = DashboardServer()
        server.app.config['TESTING'] = True
        yield server.app

@pytest.fixture
def client(flask_app):
    """Flask test client"""
    return flask_app.test_client()

@pytest.fixture
def dashboard_server(mock_config):
    """Dashboard server instance for testing"""
    with patch('src.dashboard_server.config', mock_config):
        server = DashboardServer()
        yield server

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup after each test"""
    yield
    # Clean up any test files that might have been created
    for test_dir in [TEST_UPLOAD_DIR, TEST_REPORTS_DIR, TEST_TEMPLATES_DIR]:
        if test_dir.exists():
            for file in test_dir.glob('*'):
                if file.is_file():
                    file.unlink()

@pytest.fixture
def mock_file_upload():
    """Mock file upload data"""
    return {
        'filename': 'test_contract.docx',
        'content_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'size': 1024
    }

@pytest.fixture
def sample_contract_data():
    """Sample contract data for testing"""
    return {
        'id': 'test-contract-123',
        'name': 'Test Contract.docx',
        'path': str(TEST_DATA_DIR / 'test_contract.docx'),
        'type': 'Generic',
        'size': 1024,
        'uploaded': '2025-01-01T00:00:00Z'
    }

@pytest.fixture
def sample_template_data():
    """Sample template data for testing"""
    return {
        'id': 'test-template-123',
        'name': 'Test Template.docx',
        'path': str(TEST_DATA_DIR / 'test_template.docx'),
        'category': 'Generic',
        'size': 1024,
        'uploaded': '2025-01-01T00:00:00Z'
    }

@pytest.fixture
def sample_analysis_data():
    """Sample analysis data for testing"""
    return {
        'id': 'test-analysis-123',
        'contract': 'Test Contract.docx',
        'contract_path': str(TEST_DATA_DIR / 'test_contract.docx'),
        'template': 'Test Template.docx',
        'template_path': str(TEST_DATA_DIR / 'test_template.docx'),
        'status': 'Changes - Minor',
        'changes': 5,
        'similarity': 85.5,
        'date': '2025-01-01T00:00:00Z',
        'analysis': [
            {
                'explanation': 'Filled placeholder with actual value',
                'classification': 'INCONSEQUENTIAL',
                'category': 'ADMINISTRATIVE',
                'financial_impact': 'NONE',
                'required_reviews': ['ROUTINE'],
                'procurement_flags': [],
                'review_priority': 'normal',
                'confidence': 'high'
            }
        ]
    }

# Test data generators
def generate_test_contract_text(placeholders=None):
    """Generate test contract text with optional placeholders"""
    if placeholders is None:
        placeholders = {
            'company_name': 'Test Company Inc.',
            'date': 'January 1, 2025',
            'amount': '$1,000'
        }
    
    return f"""
    CONSULTING AGREEMENT
    
    This agreement is made on {placeholders['date']} between {placeholders['company_name']}
    and the service provider.
    
    The total compensation will be {placeholders['amount']} for the services provided.
    """

def generate_test_template_text():
    """Generate test template text with placeholders"""
    return """
    CONSULTING AGREEMENT
    
    This agreement is made on [DATE] between [COMPANY_NAME]
    and the service provider.
    
    The total compensation will be [AMOUNT] for the services provided.
    """