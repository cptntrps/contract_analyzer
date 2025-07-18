"""
End-to-end tests for complete contract analysis workflows
"""

import pytest
import json
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from io import BytesIO

from app.dashboard_server import DashboardServer
from app.services.analyzer import ContractAnalyzer
from app.services.llm.handler import LLMHandler
from app.reports.enhanced_report_generator import EnhancedReportGenerator


class TestCompleteContractWorkflow:
    """Test suite for complete contract analysis workflow"""

    def test_full_contract_analysis_workflow(self, client, dashboard_server, test_docx_file, test_template_file):
        """Test the complete workflow from upload to report generation"""
        
        # Step 1: Upload template
        with open(test_template_file, 'rb') as f:
            template_response = client.post('/api/upload-template', data={
                'file': (f, 'test_template.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            })
        
        assert template_response.status_code == 200
        template_data = json.loads(template_response.data)
        template_id = template_data['template']['id']
        
        # Step 2: Upload contract
        with open(test_docx_file, 'rb') as f:
            contract_response = client.post('/api/upload-contract', data={
                'file': (f, 'test_contract.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            })
        
        assert contract_response.status_code == 200
        contract_data = json.loads(contract_response.data)
        contract_id = contract_data['contract']['id']
        
        # Step 3: Analyze contract
        analysis_response = client.post('/api/analyze-contract', 
                                      json={'contract_id': contract_id})
        
        assert analysis_response.status_code == 200
        analysis_data = json.loads(analysis_response.data)
        assert analysis_data['success'] is True
        result_id = analysis_data['result']['id']
        
        # Step 4: Generate redlined document
        redlined_response = client.post('/api/generate-redlined-document', 
                                      json={'result_id': result_id})
        
        assert redlined_response.status_code == 200
        redlined_data = json.loads(redlined_response.data)
        assert redlined_data['success'] is True
        
        # Step 5: Generate changes table
        changes_response = client.post('/api/generate-changes-table', 
                                     json={'result_id': result_id})
        
        assert changes_response.status_code == 200
        changes_data = json.loads(changes_response.data)
        assert changes_data['success'] is True
        
        # Step 6: Verify analysis results
        results_response = client.get('/api/analysis-results')
        assert results_response.status_code == 200
        results_data = json.loads(results_response.data)
        assert len(results_data) == 1
        assert results_data[0]['id'] == result_id

    def test_batch_analysis_workflow(self, client, dashboard_server, test_docx_file, test_template_file):
        """Test batch analysis workflow with multiple contracts"""
        
        # Upload template
        with open(test_template_file, 'rb') as f:
            template_response = client.post('/api/upload-template', data={
                'file': (f, 'batch_template.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            })
        
        assert template_response.status_code == 200
        
        # Upload multiple contracts
        contract_ids = []
        for i in range(3):
            with open(test_docx_file, 'rb') as f:
                contract_response = client.post('/api/upload-contract', data={
                    'file': (f, f'batch_contract_{i}.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                })
            
            assert contract_response.status_code == 200
            contract_data = json.loads(contract_response.data)
            contract_ids.append(contract_data['contract']['id'])
        
        # Perform batch analysis
        batch_response = client.post('/api/batch-analyze')
        
        assert batch_response.status_code == 200
        batch_data = json.loads(batch_response.data)
        assert batch_data['success'] is True
        assert len(batch_data['results']) == 3
        
        # Verify all contracts were analyzed
        results_response = client.get('/api/analysis-results')
        assert results_response.status_code == 200
        results_data = json.loads(results_response.data)
        assert len(results_data) == 3

    def test_multi_stakeholder_analysis_workflow(self, client, dashboard_server, mock_llm_handler):
        """Test workflow with multi-stakeholder analysis results"""
        
        # Mock multi-stakeholder analysis result
        mock_analysis_result = {
            'explanation': 'Complex pricing and legal terms change',
            'category': 'FINANCIAL',
            'classification': 'CRITICAL',
            'financial_impact': 'DIRECT',
            'required_reviews': ['FINANCE_APPROVAL', 'LEGAL_REVIEW', 'EXEC_APPROVAL'],
            'procurement_flags': ['high_value_change', 'legal_risk', 'executive_approval_required'],
            'review_priority': 'urgent',
            'deleted_text': '$50,000 standard terms',
            'inserted_text': '$75,000 with enhanced liability protection',
            'confidence': 'high'
        }
        
        mock_llm_handler.get_change_analysis.return_value = mock_analysis_result
        
        # Replace the LLM handler in dashboard server
        dashboard_server.llm_handler = mock_llm_handler
        
        # Create sample contract and template
        contract_data = {
            'id': 'multi-stakeholder-contract',
            'name': 'complex_contract.docx',
            'path': '/tmp/complex_contract.docx',
            'type': 'Procurement',
            'size': 2048,
            'uploaded': '2025-01-01T00:00:00Z'
        }
        
        template_data = {
            'id': 'multi-stakeholder-template',
            'name': 'complex_template.docx',
            'path': '/tmp/complex_template.docx',
            'category': 'Procurement',
            'size': 2048,
            'uploaded': '2025-01-01T00:00:00Z'
        }
        
        dashboard_server.contracts.append(contract_data)
        dashboard_server.templates.append(template_data)
        
        # Analyze the contract
        analysis_response = client.post('/api/analyze-contract', 
                                      json={'contract_id': contract_data['id']})
        
        assert analysis_response.status_code == 200
        analysis_data = json.loads(analysis_response.data)
        assert analysis_data['success'] is True
        
        # Verify multi-stakeholder data in results
        results_response = client.get('/api/analysis-results')
        assert results_response.status_code == 200
        results_data = json.loads(results_response.data)
        
        assert len(results_data) == 1
        result = results_data[0]
        
        # Check that analysis contains multi-stakeholder information
        assert 'analysis' in result
        assert len(result['analysis']) > 0
        
        # The analysis should contain the multi-stakeholder result
        analysis_item = result['analysis'][0]
        assert analysis_item['required_reviews'] == ['FINANCE_APPROVAL', 'LEGAL_REVIEW', 'EXEC_APPROVAL']
        assert analysis_item['procurement_flags'] == ['high_value_change', 'legal_risk', 'executive_approval_required']
        assert analysis_item['review_priority'] == 'urgent'

    def test_error_recovery_workflow(self, client, dashboard_server, test_docx_file):
        """Test error recovery in workflow"""
        
        # Upload contract
        with open(test_docx_file, 'rb') as f:
            contract_response = client.post('/api/upload-contract', data={
                'file': (f, 'error_test_contract.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            })
        
        assert contract_response.status_code == 200
        contract_data = json.loads(contract_response.data)
        contract_id = contract_data['contract']['id']
        
        # Try to analyze without template (should handle gracefully)
        analysis_response = client.post('/api/analyze-contract', 
                                      json={'contract_id': contract_id})
        
        # Should either succeed with fallback or provide meaningful error
        assert analysis_response.status_code in [200, 400]
        
        if analysis_response.status_code == 200:
            analysis_data = json.loads(analysis_response.data)
            assert analysis_data['success'] is True
        else:
            error_data = json.loads(analysis_response.data)
            assert 'error' in error_data
            assert 'template' in error_data['error'].lower()

    def test_model_switching_workflow(self, client, dashboard_server):
        """Test model switching during analysis workflow"""
        
        # Get initial model info
        initial_model_response = client.get('/api/model-info')
        assert initial_model_response.status_code == 200
        initial_model_data = json.loads(initial_model_response.data)
        initial_model = initial_model_data['name']
        
        # Get available models
        models_response = client.get('/api/available-models')
        assert models_response.status_code == 200
        models_data = json.loads(models_response.data)
        
        if len(models_data) > 1:
            # Find a different model
            target_model = None
            for model in models_data:
                if model['name'] != initial_model:
                    target_model = model['name']
                    break
            
            if target_model:
                # Switch to different model
                switch_response = client.post('/api/change-model', 
                                            json={'model': target_model})
                
                assert switch_response.status_code == 200
                switch_data = json.loads(switch_response.data)
                assert switch_data['success'] is True
                assert switch_data['current_model'] == target_model
                
                # Verify model was changed
                verify_response = client.get('/api/model-info')
                assert verify_response.status_code == 200
                verify_data = json.loads(verify_response.data)
                assert verify_data['name'] == target_model
                
                # Switch back to original model
                restore_response = client.post('/api/change-model', 
                                             json={'model': initial_model})
                
                assert restore_response.status_code == 200
                restore_data = json.loads(restore_response.data)
                assert restore_data['success'] is True
                assert restore_data['current_model'] == initial_model

    def test_configuration_workflow(self, client, dashboard_server):
        """Test configuration management workflow"""
        
        # Get initial configuration
        config_response = client.get('/api/config')
        assert config_response.status_code == 200
        config_data = json.loads(config_response.data)
        initial_max_size = config_data['max_file_size']
        
        # Update configuration
        new_config = {
            'max_file_size': '32MB',
            'log_level': 'INFO'
        }
        
        update_response = client.post('/api/config', json=new_config)
        assert update_response.status_code == 200
        update_data = json.loads(update_response.data)
        assert update_data['success'] is True
        
        # Verify configuration was updated
        verify_response = client.get('/api/config')
        assert verify_response.status_code == 200
        verify_data = json.loads(verify_response.data)
        assert verify_data['max_file_size'] == '32MB'
        
        # Clear cache
        cache_response = client.post('/api/clear-cache', 
                                   json={'cache_type': 'all'})
        assert cache_response.status_code == 200
        cache_data = json.loads(cache_response.data)
        assert cache_data['success'] is True

    def test_health_monitoring_workflow(self, client, dashboard_server):
        """Test health monitoring throughout workflow"""
        
        # Check initial health
        health_response = client.get('/api/health')
        assert health_response.status_code == 200
        health_data = json.loads(health_response.data)
        assert health_data['status'] == 'healthy'
        
        # Check system info
        system_response = client.get('/api/system-info')
        assert system_response.status_code == 200
        system_data = json.loads(system_response.data)
        assert 'system' in system_data
        assert 'disk_usage' in system_data
        assert 'memory_usage' in system_data
        
        # Check model info
        model_response = client.get('/api/model-info')
        assert model_response.status_code == 200
        model_data = json.loads(model_response.data)
        assert 'name' in model_data
        assert 'provider' in model_data
        assert 'connection_healthy' in model_data

    def test_data_persistence_workflow(self, client, dashboard_server, test_docx_file, test_template_file):
        """Test data persistence across operations"""
        
        # Upload and analyze contract
        with open(test_template_file, 'rb') as f:
            template_response = client.post('/api/upload-template', data={
                'file': (f, 'persistence_template.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            })
        
        with open(test_docx_file, 'rb') as f:
            contract_response = client.post('/api/upload-contract', data={
                'file': (f, 'persistence_contract.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            })
        
        contract_data = json.loads(contract_response.data)
        contract_id = contract_data['contract']['id']
        
        analysis_response = client.post('/api/analyze-contract', 
                                      json={'contract_id': contract_id})
        
        assert analysis_response.status_code == 200
        analysis_data = json.loads(analysis_response.data)
        result_id = analysis_data['result']['id']
        
        # Verify data persistence
        contracts_response = client.get('/api/contracts')
        assert contracts_response.status_code == 200
        contracts_data = json.loads(contracts_response.data)
        assert len(contracts_data) == 1
        assert contracts_data[0]['id'] == contract_id
        
        templates_response = client.get('/api/templates')
        assert templates_response.status_code == 200
        templates_data = json.loads(templates_response.data)
        assert len(templates_data) == 1
        
        results_response = client.get('/api/analysis-results')
        assert results_response.status_code == 200
        results_data = json.loads(results_response.data)
        assert len(results_data) == 1
        assert results_data[0]['id'] == result_id

    def test_cleanup_workflow(self, client, dashboard_server, test_docx_file, test_template_file):
        """Test cleanup operations"""
        
        # Upload contract and template
        with open(test_template_file, 'rb') as f:
            template_response = client.post('/api/upload-template', data={
                'file': (f, 'cleanup_template.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            })
        
        with open(test_docx_file, 'rb') as f:
            contract_response = client.post('/api/upload-contract', data={
                'file': (f, 'cleanup_contract.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            })
        
        template_data = json.loads(template_response.data)
        contract_data = json.loads(contract_response.data)
        template_id = template_data['template']['id']
        contract_id = contract_data['contract']['id']
        
        # Verify uploads
        contracts_response = client.get('/api/contracts')
        assert len(json.loads(contracts_response.data)) == 1
        
        templates_response = client.get('/api/templates')
        assert len(json.loads(templates_response.data)) == 1
        
        # Delete contract
        delete_contract_response = client.delete(f'/api/delete-contract/{contract_id}')
        assert delete_contract_response.status_code == 200
        
        # Verify contract was deleted
        contracts_response = client.get('/api/contracts')
        assert len(json.loads(contracts_response.data)) == 0
        
        # Delete template
        delete_template_response = client.delete(f'/api/delete-template/{template_id}')
        assert delete_template_response.status_code == 200
        
        # Verify template was deleted
        templates_response = client.get('/api/templates')
        assert len(json.loads(templates_response.data)) == 0


class TestErrorScenarios:
    """Test suite for error scenarios in workflows"""

    def test_corrupted_file_workflow(self, client):
        """Test workflow with corrupted file"""
        
        # Create a corrupted DOCX file
        corrupted_file = b'This is not a valid DOCX file'
        
        response = client.post('/api/upload-contract', data={
            'file': (BytesIO(corrupted_file), 'corrupted.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        })
        
        # Should handle corrupted file gracefully
        assert response.status_code in [200, 400]
        
        if response.status_code == 400:
            data = json.loads(response.data)
            assert 'error' in data

    def test_missing_dependencies_workflow(self, client, dashboard_server):
        """Test workflow with missing dependencies"""
        
        # Mock missing LLM provider
        with patch.object(dashboard_server, 'llm_handler', None):
            # Create sample contract
            contract_data = {
                'id': 'no-llm-contract',
                'name': 'test_contract.docx',
                'path': '/tmp/test_contract.docx',
                'type': 'Generic',
                'size': 1024,
                'uploaded': '2025-01-01T00:00:00Z'
            }
            
            dashboard_server.contracts.append(contract_data)
            
            # Try to analyze without LLM
            analysis_response = client.post('/api/analyze-contract', 
                                          json={'contract_id': contract_data['id']})
            
            # Should handle missing LLM gracefully
            assert analysis_response.status_code in [200, 500]

    def test_disk_space_workflow(self, client, dashboard_server):
        """Test workflow with disk space issues"""
        
        # Mock disk space check
        with patch.object(dashboard_server, 'get_disk_usage') as mock_disk:
            mock_disk.return_value = {
                'total_gb': 100.0,
                'used_gb': 95.0,
                'free_gb': 5.0,
                'used_percent': 95.0,
                'available_percent': 5.0
            }
            
            # Check system info reflects low disk space
            system_response = client.get('/api/system-info')
            assert system_response.status_code == 200
            system_data = json.loads(system_response.data)
            assert system_data['disk_usage']['used_percent'] == 95.0

    def test_network_connectivity_workflow(self, client, dashboard_server):
        """Test workflow with network connectivity issues"""
        
        # Mock network connectivity issues
        with patch.object(dashboard_server.llm_handler, 'check_connection', return_value=False):
            # Check health reflects connectivity issues
            health_response = client.get('/api/health')
            assert health_response.status_code == 200
            health_data = json.loads(health_response.data)
            assert health_data['components']['llm']['status'] == 'unhealthy'

    def test_concurrent_operations_workflow(self, client, dashboard_server, test_docx_file):
        """Test workflow with concurrent operations"""
        
        # Simulate multiple concurrent uploads
        import threading
        results = []
        
        def upload_contract(index):
            with open(test_docx_file, 'rb') as f:
                response = client.post('/api/upload-contract', data={
                    'file': (f, f'concurrent_contract_{index}.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                })
            results.append(response.status_code)
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=upload_contract, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that all uploads succeeded
        assert all(status == 200 for status in results)
        
        # Verify all contracts were uploaded
        contracts_response = client.get('/api/contracts')
        assert contracts_response.status_code == 200
        contracts_data = json.loads(contracts_response.data)
        assert len(contracts_data) == 5