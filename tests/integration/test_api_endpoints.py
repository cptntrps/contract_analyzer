"""
Integration tests for API endpoints
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from werkzeug.datastructures import FileStorage

from src.dashboard_server import DashboardServer


class TestHealthEndpoints:
    """Test suite for health and status endpoints"""

    def test_health_endpoint(self, client):
        """Test /api/health endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert 'timestamp' in data
        assert 'version' in data
        assert 'components' in data

    def test_model_info_endpoint(self, client):
        """Test /api/model-info endpoint"""
        response = client.get('/api/model-info')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'name' in data
        assert 'provider' in data
        assert 'available_models' in data
        assert 'connection_healthy' in data

    def test_system_info_endpoint(self, client):
        """Test /api/system-info endpoint"""
        response = client.get('/api/system-info')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'system' in data
        assert 'disk_usage' in data
        assert 'memory_usage' in data
        assert 'recent_activity' in data


class TestContractEndpoints:
    """Test suite for contract management endpoints"""

    def test_get_contracts_empty(self, client):
        """Test GET /api/contracts with no contracts"""
        response = client.get('/api/contracts')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_upload_contract_success(self, client, test_docx_file):
        """Test successful contract upload"""
        with open(test_docx_file, 'rb') as f:
            response = client.post('/api/upload-contract', data={
                'file': (f, 'test_contract.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'contract' in data
        assert data['contract']['name'] == 'test_contract.docx'

    def test_upload_contract_invalid_file_type(self, client):
        """Test contract upload with invalid file type"""
        file_data = BytesIO(b'invalid content')
        response = client.post('/api/upload-contract', data={
            'file': (file_data, 'test.txt', 'text/plain')
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'file type' in data['error'].lower()

    def test_upload_contract_no_file(self, client):
        """Test contract upload without file"""
        response = client.post('/api/upload-contract', data={})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'no file' in data['error'].lower()

    def test_delete_contract_success(self, client, dashboard_server, sample_contract_data):
        """Test successful contract deletion"""
        # Add contract to server
        dashboard_server.contracts.append(sample_contract_data)
        
        response = client.delete(f'/api/delete-contract/{sample_contract_data["id"]}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'deleted' in data['message'].lower()

    def test_delete_contract_not_found(self, client):
        """Test contract deletion with non-existent ID"""
        response = client.delete('/api/delete-contract/nonexistent-id')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'not found' in data['error'].lower()

    def test_get_contracts_with_data(self, client, dashboard_server, sample_contract_data):
        """Test GET /api/contracts with contract data"""
        dashboard_server.contracts.append(sample_contract_data)
        
        response = client.get('/api/contracts')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['name'] == sample_contract_data['name']


class TestTemplateEndpoints:
    """Test suite for template management endpoints"""

    def test_get_templates_empty(self, client):
        """Test GET /api/templates with no templates"""
        response = client.get('/api/templates')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_upload_template_success(self, client, test_template_file):
        """Test successful template upload"""
        with open(test_template_file, 'rb') as f:
            response = client.post('/api/upload-template', data={
                'file': (f, 'test_template.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'template' in data
        assert data['template']['name'] == 'test_template.docx'

    def test_upload_template_invalid_file_type(self, client):
        """Test template upload with invalid file type"""
        file_data = BytesIO(b'invalid content')
        response = client.post('/api/upload-template', data={
            'file': (file_data, 'test.txt', 'text/plain')
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_delete_template_success(self, client, dashboard_server, sample_template_data):
        """Test successful template deletion"""
        # Add template to server
        dashboard_server.templates.append(sample_template_data)
        
        response = client.delete(f'/api/delete-template/{sample_template_data["id"]}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

    def test_delete_template_not_found(self, client):
        """Test template deletion with non-existent ID"""
        response = client.delete('/api/delete-template/nonexistent-id')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data


class TestAnalysisEndpoints:
    """Test suite for analysis endpoints"""

    def test_get_analysis_results_empty(self, client):
        """Test GET /api/analysis-results with no results"""
        response = client.get('/api/analysis-results')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_analyze_contract_success(self, client, dashboard_server, sample_contract_data, sample_template_data):
        """Test successful contract analysis"""
        # Add contract and template to server
        dashboard_server.contracts.append(sample_contract_data)
        dashboard_server.templates.append(sample_template_data)
        
        # Mock the analysis process
        with patch.object(dashboard_server, 'run_contract_analysis') as mock_analysis:
            mock_analysis.return_value = {
                'id': 'test-analysis-123',
                'contract': sample_contract_data['name'],
                'template': sample_template_data['name'],
                'status': 'Changes - Minor',
                'changes': 3,
                'similarity': 90.0
            }
            
            response = client.post('/api/analyze-contract', 
                                 json={'contract_id': sample_contract_data['id']})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'result' in data
            assert data['result']['contract'] == sample_contract_data['name']

    def test_analyze_contract_not_found(self, client):
        """Test contract analysis with non-existent contract"""
        response = client.post('/api/analyze-contract', 
                             json={'contract_id': 'nonexistent-id'})
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'not found' in data['error'].lower()

    def test_analyze_contract_missing_id(self, client):
        """Test contract analysis without contract ID"""
        response = client.post('/api/analyze-contract', json={})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'required' in data['error'].lower()

    def test_batch_analyze_success(self, client, dashboard_server, sample_contract_data, sample_template_data):
        """Test successful batch analysis"""
        # Add contract and template to server
        dashboard_server.contracts.append(sample_contract_data)
        dashboard_server.templates.append(sample_template_data)
        
        # Mock the analysis process
        with patch.object(dashboard_server, 'run_contract_analysis') as mock_analysis:
            mock_analysis.return_value = {
                'id': 'test-analysis-123',
                'contract': sample_contract_data['name'],
                'template': sample_template_data['name'],
                'status': 'Changes - Minor',
                'changes': 3,
                'similarity': 90.0
            }
            
            response = client.post('/api/batch-analyze')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'results' in data
            assert len(data['results']) == 1

    def test_batch_analyze_empty_contracts(self, client):
        """Test batch analysis with no contracts"""
        response = client.post('/api/batch-analyze')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['results'] == []

    def test_get_analysis_results_with_data(self, client, dashboard_server, sample_analysis_data):
        """Test GET /api/analysis-results with analysis data"""
        dashboard_server.analysis_results.append(sample_analysis_data)
        
        response = client.get('/api/analysis-results')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['contract'] == sample_analysis_data['contract']


class TestReportGenerationEndpoints:
    """Test suite for report generation endpoints"""

    def test_generate_redlined_document_success(self, client, dashboard_server, sample_analysis_data):
        """Test successful redlined document generation"""
        dashboard_server.analysis_results.append(sample_analysis_data)
        
        # Mock the report generator
        with patch.object(dashboard_server.report_generator, 'generate_review_document') as mock_generate:
            mock_generate.return_value = '/path/to/redlined.docx'
            
            response = client.post('/api/generate-redlined-document', 
                                 json={'result_id': sample_analysis_data['id']})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'file_path' in data

    def test_generate_redlined_document_not_found(self, client):
        """Test redlined document generation with non-existent result"""
        response = client.post('/api/generate-redlined-document', 
                             json={'result_id': 'nonexistent-id'})
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'not found' in data['error'].lower()

    def test_generate_changes_table_success(self, client, dashboard_server, sample_analysis_data):
        """Test successful changes table generation"""
        dashboard_server.analysis_results.append(sample_analysis_data)
        
        # Mock the report generator
        with patch.object(dashboard_server.report_generator, 'generate_changes_table_xlsx') as mock_generate:
            mock_generate.return_value = '/path/to/changes.xlsx'
            
            response = client.post('/api/generate-changes-table', 
                                 json={'result_id': sample_analysis_data['id']})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'file_path' in data


    def test_generate_word_com_redlined_success(self, client, dashboard_server, sample_analysis_data):
        """Test successful Word COM redlined document generation"""
        dashboard_server.analysis_results.append(sample_analysis_data)
        
        # Mock the report generator
        with patch.object(dashboard_server.report_generator, 'generate_word_com_redlined_document') as mock_generate:
            mock_generate.return_value = '/path/to/redlined_com.docx'
            
            response = client.post('/api/generate-word-com-redlined', 
                                 json={'result_id': sample_analysis_data['id']})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'file_path' in data

    def test_generate_word_com_redlined_not_available(self, client, dashboard_server, sample_analysis_data):
        """Test Word COM redlined document generation when not available"""
        dashboard_server.analysis_results.append(sample_analysis_data)
        
        # Mock the report generator to return None (COM not available)
        with patch.object(dashboard_server.report_generator, 'generate_word_com_redlined_document') as mock_generate:
            mock_generate.return_value = None
            
            response = client.post('/api/generate-word-com-redlined', 
                                 json={'result_id': sample_analysis_data['id']})
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'not available' in data['error'].lower()


class TestModelManagementEndpoints:
    """Test suite for model management endpoints"""

    def test_change_model_success(self, client, dashboard_server):
        """Test successful model change"""
        # Mock the LLM handler
        with patch.object(dashboard_server.llm_handler, 'change_model') as mock_change:
            mock_change.return_value = {
                'success': True,
                'message': 'Model changed successfully',
                'current_model': 'gpt-4o',
                'previous_model': 'gpt-3.5-turbo'
            }
            
            response = client.post('/api/change-model', 
                                 json={'model': 'gpt-4o'})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['current_model'] == 'gpt-4o'
            assert data['previous_model'] == 'gpt-3.5-turbo'

    def test_change_model_failure(self, client, dashboard_server):
        """Test model change failure"""
        # Mock the LLM handler
        with patch.object(dashboard_server.llm_handler, 'change_model') as mock_change:
            mock_change.return_value = {
                'success': False,
                'message': 'Model not available',
                'current_model': 'gpt-3.5-turbo'
            }
            
            response = client.post('/api/change-model', 
                                 json={'model': 'invalid-model'})
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'not available' in data['message'].lower()

    def test_change_model_missing_model(self, client):
        """Test model change without model parameter"""
        response = client.post('/api/change-model', json={})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'required' in data['error'].lower()

    def test_get_available_models(self, client, dashboard_server):
        """Test getting available models"""
        # Mock the LLM handler
        with patch.object(dashboard_server.llm_handler, 'get_available_models') as mock_models:
            mock_models.return_value = [
                {'name': 'gpt-4o', 'description': 'GPT-4 Omni'},
                {'name': 'gpt-3.5-turbo', 'description': 'GPT-3.5 Turbo'}
            ]
            
            response = client.get('/api/available-models')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]['name'] == 'gpt-4o'


class TestConfigurationEndpoints:
    """Test suite for configuration endpoints"""

    def test_get_config_success(self, client):
        """Test getting configuration"""
        response = client.get('/api/config')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, dict)
        assert 'upload_folder' in data
        assert 'max_file_size' in data
        assert 'allowed_extensions' in data

    def test_update_config_success(self, client):
        """Test updating configuration"""
        config_update = {
            'max_file_size': '32MB',
            'log_level': 'INFO'
        }
        
        response = client.post('/api/config', json=config_update)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'updated' in data['message'].lower()

    def test_clear_cache_success(self, client, dashboard_server):
        """Test cache clearing"""
        # Mock the cache clearing
        with patch.object(dashboard_server, 'clear_cache') as mock_clear:
            mock_clear.return_value = {
                'success': True,
                'message': 'Cache cleared successfully',
                'details': {'memory_cleared': True, 'files_cleared': True}
            }
            
            response = client.post('/api/clear-cache', 
                                 json={'cache_type': 'all'})
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'cleared' in data['message'].lower()


class TestSecurityAndValidation:
    """Test suite for security and validation"""

    def test_file_upload_security(self, client):
        """Test file upload security validation"""
        # Test with potentially malicious filename
        malicious_file = BytesIO(b'malicious content')
        response = client.post('/api/upload-contract', data={
            'file': (malicious_file, '../../../etc/passwd', 'text/plain')
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_path_traversal_protection(self, client):
        """Test protection against path traversal attacks"""
        response = client.delete('/api/delete-contract/../../../etc/passwd')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_sql_injection_protection(self, client):
        """Test protection against SQL injection-like attacks"""
        response = client.post('/api/analyze-contract', 
                             json={'contract_id': "'; DROP TABLE contracts; --"})
        
        assert response.status_code == 404  # Should be treated as normal not found
        data = json.loads(response.data)
        assert 'error' in data

    def test_xss_protection(self, client):
        """Test protection against XSS attacks"""
        xss_payload = "<script>alert('xss')</script>"
        response = client.post('/api/analyze-contract', 
                             json={'contract_id': xss_payload})
        
        assert response.status_code == 404  # Should be treated as normal not found
        data = json.loads(response.data)
        assert 'error' in data

    def test_large_file_upload_protection(self, client):
        """Test protection against large file uploads"""
        # Create a large file that exceeds limits
        large_file = BytesIO(b'x' * (20 * 1024 * 1024))  # 20MB
        response = client.post('/api/upload-contract', data={
            'file': (large_file, 'large_file.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        })
        
        assert response.status_code == 413  # Request Entity Too Large


class TestErrorHandling:
    """Test suite for error handling"""

    def test_404_error_handler(self, client):
        """Test 404 error handling"""
        response = client.get('/api/nonexistent-endpoint')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
        assert '404' in data['error'] or 'not found' in data['error'].lower()

    def test_405_error_handler(self, client):
        """Test 405 Method Not Allowed error handling"""
        response = client.post('/api/health')  # GET endpoint accessed with POST
        assert response.status_code == 405
        
        data = json.loads(response.data)
        assert 'error' in data
        assert '405' in data['error'] or 'method not allowed' in data['error'].lower()

    def test_500_error_handler(self, client, dashboard_server):
        """Test 500 Internal Server Error handling"""
        # Mock a method to raise an exception
        with patch.object(dashboard_server, 'run_contract_analysis', side_effect=Exception("Test error")):
            dashboard_server.contracts.append({'id': 'test-id', 'name': 'test.docx'})
            
            response = client.post('/api/analyze-contract', 
                                 json={'contract_id': 'test-id'})
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data

    def test_malformed_json_handling(self, client):
        """Test handling of malformed JSON"""
        response = client.post('/api/analyze-contract', 
                             data='{"invalid": json}',
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_missing_content_type_handling(self, client):
        """Test handling of missing content type"""
        response = client.post('/api/analyze-contract', 
                             data='{"contract_id": "test"}')
        
        # Should still work or provide appropriate error
        assert response.status_code in [200, 400, 404]