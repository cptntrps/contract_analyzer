"""
Unit tests for LLM providers and enhanced redlining functionality

DEPRECATED: This test file is deprecated and needs complete rewrite.
The old LLMHandler class has been replaced with provider-based architecture.
This file contains 50+ tests that are all broken due to architectural changes.

TODO: Create new test files for:
- app/services/llm/providers/base.py
- app/services/llm/providers/openai.py
- Any new LLM handler classes in the new architecture

This file should be deleted once new tests are created.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

from app.services.llm.providers.base import BaseLLMProvider, LLMError, LLMConnectionError, LLMAnalysisError
from app.services.llm.providers.openai import OpenAIProvider


class TestLLMHandler:
    """Test suite for LLMHandler class"""

    def test_init_with_mock_provider(self, mock_openai_provider):
        """Test LLMHandler initialization with mock provider"""
        with patch('app.services.llm.providers.openai.OpenAIProvider', return_value=mock_openai_provider):
            provider = mock_openai_provider
            assert provider is not None
            assert handler._provider_type == 'openai'  # Default from config

    def test_init_with_provider_failure(self):
        """Test LLMHandler initialization with provider failure"""
        with patch('app.services.llm.provider_factory.create_llm_provider', side_effect=Exception("Provider failed")):
            handler = LLMHandler()
            assert handler is not None
            assert handler._provider is None
            assert handler._provider_type == 'openai'

    def test_get_available_models_success(self, mock_openai_provider):
        """Test getting available models successfully"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            models = handler.get_available_models()
            assert isinstance(models, list)
            assert len(models) > 0
            mock_openai_provider.get_available_models.assert_called_once()

    def test_get_available_models_no_provider(self):
        """Test getting available models without provider"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            models = handler.get_available_models()
            assert isinstance(models, list)
            assert len(models) == 0

    def test_get_available_models_exception(self, mock_openai_provider):
        """Test getting available models with exception"""
        mock_openai_provider.get_available_models.side_effect = Exception("Connection failed")
        
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            models = handler.get_available_models()
            assert isinstance(models, list)
            assert len(models) == 0

    def test_change_model_success(self, mock_openai_provider):
        """Test successful model change"""
        mock_openai_provider.change_model.return_value = {
            'success': True,
            'message': 'Model changed successfully',
            'current_model': 'new-model'
        }
        
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            result = handler.change_model('new-model')
            
            assert result['success'] is True
            assert 'message' in result
            assert result['current_model'] == 'new-model'
            mock_openai_provider.change_model.assert_called_once_with('new-model')

    def test_change_model_no_provider(self):
        """Test model change without provider"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            result = handler.change_model('new-model')
            
            assert result['success'] is False
            assert 'No provider available' in result['message']

    def test_change_model_exception(self, mock_openai_provider):
        """Test model change with exception"""
        mock_openai_provider.change_model.side_effect = Exception("Change failed")
        
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            result = handler.change_model('new-model')
            
            assert result['success'] is False
            assert 'Model change error' in result['message']

    def test_get_current_model_success(self, mock_openai_provider):
        """Test getting current model successfully"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            model = handler.get_current_model()
            assert model == 'gpt-4o'
            # Called once during init and once during test
            assert mock_openai_provider.get_current_model.call_count >= 1

    def test_get_current_model_no_provider(self):
        """Test getting current model without provider"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            with patch('app.config.user_settings.get_llm_config', return_value={'openai_model': 'fallback-model'}):
                handler = LLMHandler()
                model = handler.get_current_model()
                assert model == 'fallback-model'

    def test_get_model_info_success(self, mock_openai_provider):
        """Test getting model info successfully"""
        mock_openai_provider.get_available_models.return_value = [
            {'name': 'gpt-4o', 'description': 'Test model'}
        ]
        
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            info = handler.get_model_info()
            
            assert isinstance(info, dict)
            assert info['name'] == 'gpt-4o'
            assert info['provider'] == 'openai'
            assert 'available_models' in info

    def test_check_connection_success(self, mock_openai_provider):
        """Test successful connection check"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            result = handler.check_connection()
            assert result is True
            mock_openai_provider.check_connection.assert_called_once()

    def test_check_connection_no_provider(self):
        """Test connection check without provider"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            result = handler.check_connection()
            assert result is False

    def test_check_connection_exception(self, mock_openai_provider):
        """Test connection check with exception"""
        mock_openai_provider.check_connection.side_effect = Exception("Connection failed")
        
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            result = handler.check_connection()
            assert result is False


class TestLLMAnalysisFunctionality:
    """Test suite for LLM analysis functionality"""

    def test_get_change_analysis_success(self, mock_openai_provider):
        """Test successful change analysis"""
        mock_response = {
            "explanation": "Updated rate from placeholder to actual value",
            "category": "FINANCIAL",
            "classification": "SIGNIFICANT",
            "financial_impact": "DIRECT",
            "required_reviews": ["FINANCE_APPROVAL", "LEGAL_REVIEW"],
            "procurement_flags": ["rate_change"],
            "confidence": "high",
            "review_priority": "urgent"
        }
        
        mock_openai_provider._generate_response.return_value = json.dumps(mock_response)
        
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            
            result = handler.get_change_analysis(
                deleted_text="$[HOURLY_RATE]",
                inserted_text="$150"
            )
            
            assert isinstance(result, dict)
            assert result['explanation'] == "Updated rate from placeholder to actual value"
            assert result['category'] == "FINANCIAL"
            assert result['classification'] == "SIGNIFICANT"
            assert result['financial_impact'] == "DIRECT"
            assert result['required_reviews'] == ["FINANCE_APPROVAL", "LEGAL_REVIEW"]
            assert result['procurement_flags'] == ["rate_change"]
            assert result['confidence'] == "high"
            assert result['review_priority'] == "urgent"

    def test_get_change_analysis_no_connection(self):
        """Test change analysis without connection"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            result = handler.get_change_analysis(
                deleted_text="$[HOURLY_RATE]",
                inserted_text="$150"
            )
            
            assert isinstance(result, dict)
            assert result['confidence'] == 'low'
            # Check that fallback analysis was used (explanation contains expected text)
            assert len(result['explanation']) > 0

    def test_get_change_analysis_empty_changes(self, mock_openai_provider):
        """Test change analysis with empty changes"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            
            result = handler.get_change_analysis(
                deleted_text="",
                inserted_text=""
            )
            
            assert isinstance(result, dict)
            assert result['explanation'] == "No changes detected"
            assert result['classification'] == 'INCONSEQUENTIAL'
            assert result['confidence'] == 'high'

    def test_parse_analysis_response_valid_json(self):
        """Test parsing valid JSON response"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            json_response = {
                "explanation": "Test explanation",
                "category": "FINANCIAL",
                "classification": "SIGNIFICANT",
                "financial_impact": "DIRECT",
                "required_reviews": ["FINANCE_APPROVAL"],
                "procurement_flags": ["test_flag"],
                "confidence": "high",
                "review_priority": "normal"
            }
            
            result = handler._parse_analysis_response(
                json.dumps(json_response),
                "deleted",
                "inserted"
            )
            
            assert result['explanation'] == "Test explanation"
            assert result['category'] == "FINANCIAL"
            assert result['classification'] == "SIGNIFICANT"
            assert result['financial_impact'] == "DIRECT"
            assert result['required_reviews'] == ["FINANCE_APPROVAL"]
            assert result['procurement_flags'] == ["test_flag"]
            assert result['deleted_text'] == "deleted"
            assert result['inserted_text'] == "inserted"

    def test_parse_analysis_response_invalid_json(self):
        """Test parsing invalid JSON response"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            result = handler._parse_analysis_response(
                "invalid json response",
                "deleted",
                "inserted"
            )
            
            assert isinstance(result, dict)
            assert result['confidence'] == 'low'
            # Check that fallback analysis was used (explanation contains expected text)
            assert len(result['explanation']) > 0

    def test_parse_analysis_response_legacy_format(self):
        """Test parsing legacy format response"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            legacy_response = """
            EXPLANATION: This is a legacy format explanation
            CLASSIFICATION: SIGNIFICANT
            """
            
            result = handler._parse_analysis_response(
                legacy_response,
                "deleted",
                "inserted"
            )
            
            assert isinstance(result, dict)
            assert "legacy format explanation" in result['explanation']
            assert result['classification'] == "SIGNIFICANT"

    def test_create_fallback_analysis_financial(self):
        """Test fallback analysis for financial changes"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            result = handler._create_fallback_analysis(
                "$[AMOUNT]",
                "$1,000 payment terms"
            )
            
            assert isinstance(result, dict)
            assert 'FINANCE_APPROVAL' in result['required_reviews']
            assert result['financial_impact'] == 'INDIRECT'
            assert result['review_priority'] == 'normal'

    def test_create_fallback_analysis_legal(self):
        """Test fallback analysis for legal changes"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            result = handler._create_fallback_analysis(
                "[LIABILITY_CLAUSE]",
                "Company shall not be liable for any damages"
            )
            
            assert isinstance(result, dict)
            assert 'LEGAL_REVIEW' in result['required_reviews']

    def test_create_fallback_analysis_multi_stakeholder(self):
        """Test fallback analysis with multiple stakeholders"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            result = handler._create_fallback_analysis(
                "[PAYMENT_TERMS]",
                "Payment of $50,000 due within 30 days with legal liability"
            )
            
            assert isinstance(result, dict)
            assert 'FINANCE_APPROVAL' in result['required_reviews']
            assert 'LEGAL_REVIEW' in result['required_reviews']
            assert len(result['required_reviews']) >= 2

    def test_fallback_classification_placeholder_to_actual(self):
        """Test fallback classification for placeholder to actual content"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            result = handler._fallback_classification(
                "[COMPANY_NAME]",
                "Acme Corporation"
            )
            
            assert result == 'INCONSEQUENTIAL'

    def test_fallback_classification_actual_to_actual(self):
        """Test fallback classification for actual to actual content"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            result = handler._fallback_classification(
                "Company A",
                "Company B"
            )
            
            assert result == 'CRITICAL'

    def test_fallback_classification_monetary_values(self):
        """Test fallback classification for monetary values"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            result = handler._fallback_classification(
                "$1,000",
                "$2,000"
            )
            
            assert result == 'CRITICAL'

    def test_analyze_changes_batch(self, mock_openai_provider):
        """Test analyzing multiple changes in batch"""
        mock_response = {
            "explanation": "Test analysis",
            "category": "ADMINISTRATIVE",
            "classification": "INCONSEQUENTIAL",
            "financial_impact": "NONE",
            "required_reviews": ["ROUTINE"],
            "procurement_flags": [],
            "confidence": "high",
            "review_priority": "normal"
        }
        
        mock_openai_provider._generate_response.return_value = json.dumps(mock_response)
        
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            
            changes = [
                ('delete', 'old text 1'),
                ('insert', 'new text 1'),
                ('delete', 'old text 2'),
                ('insert', 'new text 2')
            ]
            
            results = handler.analyze_changes(changes)
            
            assert isinstance(results, list)
            assert len(results) == 2  # Two pairs of changes
            
            for result in results:
                assert isinstance(result, dict)
                assert 'explanation' in result
                assert 'classification' in result
                assert 'required_reviews' in result

    def test_get_health_status_success(self, mock_openai_provider):
        """Test getting health status successfully"""
        mock_openai_provider.get_health_status.return_value = {
            'connection_healthy': True,
            'analysis_functional': True,
            'status': 'healthy'
        }
        
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            status = handler.get_health_status()
            
            assert isinstance(status, dict)
            assert status['connection_healthy'] is True
            assert status['analysis_functional'] is True
            assert status['status'] == 'healthy'

    def test_get_health_status_no_provider(self):
        """Test getting health status without provider"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            status = handler.get_health_status()
            
            assert isinstance(status, dict)
            assert status['connection_healthy'] is False
            assert status['analysis_functional'] is False
            assert status['status'] == 'unhealthy'
            assert 'No provider available' in status['error']


class TestLLMErrorHandling:
    """Test suite for LLM error handling"""

    def test_llm_error_inheritance(self):
        """Test LLM error class inheritance"""
        error = LLMError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    def test_llm_connection_error_inheritance(self):
        """Test LLM connection error class inheritance"""
        error = LLMConnectionError("Connection failed")
        assert isinstance(error, LLMError)
        assert isinstance(error, Exception)
        assert str(error) == "Connection failed"

    def test_llm_analysis_error_inheritance(self):
        """Test LLM analysis error class inheritance"""
        error = LLMAnalysisError("Analysis failed")
        assert isinstance(error, LLMError)
        assert isinstance(error, Exception)
        assert str(error) == "Analysis failed"

    def test_retry_with_backoff_success(self, mock_openai_provider):
        """Test retry mechanism with successful execution"""
        mock_func = Mock(return_value="success")
        
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            handler.max_retries = 3
            handler.retry_delay = 0.1
            
            result = handler._retry_with_backoff(mock_func, "arg1", kwarg1="value1")
            
            assert result == "success"
            mock_func.assert_called_once_with("arg1", kwarg1="value1")

    def test_retry_with_backoff_failure(self, mock_openai_provider):
        """Test retry mechanism with failure"""
        mock_func = Mock(side_effect=LLMConnectionError("Connection failed"))
        
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            handler.max_retries = 2
            handler.retry_delay = 0.01
            
            with pytest.raises(LLMConnectionError):
                handler._retry_with_backoff(mock_func)
            
            assert mock_func.call_count == 3  # Initial + 2 retries

    def test_retry_with_backoff_eventual_success(self, mock_openai_provider):
        """Test retry mechanism with eventual success"""
        mock_func = Mock(side_effect=[
            LLMConnectionError("Failed 1"),
            LLMConnectionError("Failed 2"),
            "success"
        ])
        
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            handler.max_retries = 3
            handler.retry_delay = 0.01
            
            result = handler._retry_with_backoff(mock_func)
            
            assert result == "success"
            assert mock_func.call_count == 3


class TestEnhancedMultiStakeholderFeatures:
    """Test suite for enhanced multi-stakeholder features"""

    def test_multi_stakeholder_json_parsing(self):
        """Test parsing JSON with multiple stakeholders"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            json_response = {
                "explanation": "Complex change affecting multiple departments",
                "category": "FINANCIAL",
                "classification": "CRITICAL",
                "financial_impact": "DIRECT",
                "required_reviews": ["FINANCE_APPROVAL", "LEGAL_REVIEW", "OPS_REVIEW"],
                "procurement_flags": ["high_value_change", "compliance_risk"],
                "confidence": "high",
                "review_priority": "urgent"
            }
            
            result = handler._parse_analysis_response(
                json.dumps(json_response),
                "$50,000 with legal liability",
                "$75,000 with enhanced liability coverage"
            )
            
            assert len(result['required_reviews']) == 3
            assert 'FINANCE_APPROVAL' in result['required_reviews']
            assert 'LEGAL_REVIEW' in result['required_reviews']
            assert 'OPS_REVIEW' in result['required_reviews']
            assert len(result['procurement_flags']) == 2
            assert result['review_priority'] == 'urgent'

    def test_procurement_focused_prompt_generation(self, mock_openai_provider):
        """Test that procurement-focused prompts are generated correctly"""
        mock_openai_provider._generate_response.return_value = '{"explanation": "test"}'
        
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            
            # This should trigger the procurement-focused prompt
            handler.get_change_analysis(
                deleted_text="$[HOURLY_RATE]",
                inserted_text="$150"
            )
            
            # Verify the prompt contains procurement-specific content
            call_args = mock_openai_provider._generate_response.call_args[0][0]
            assert 'procurement contract analysis expert' in call_args
            assert 'FINANCE_APPROVAL' in call_args
            assert 'LEGAL_REVIEW' in call_args
            assert 'OPS_REVIEW' in call_args
            assert 'STAKEHOLDER TRIGGER CRITERIA' in call_args

    def test_fallback_multi_stakeholder_logic(self):
        """Test fallback logic produces multiple stakeholders when appropriate"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            # Test with text that should trigger multiple stakeholders
            result = handler._create_fallback_analysis(
                "[PAYMENT_TERMS]",
                "Payment of $50,000 due within 30 days with legal indemnification clause"
            )
            
            assert isinstance(result['required_reviews'], list)
            assert len(result['required_reviews']) >= 2
            assert 'FINANCE_APPROVAL' in result['required_reviews']
            assert 'LEGAL_REVIEW' in result['required_reviews']

    def test_procurement_flags_in_fallback(self):
        """Test that procurement flags are set in fallback analysis"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            result = handler._create_fallback_analysis(
                "[PLACEHOLDER]",
                "actual content"
            )
            
            assert isinstance(result['procurement_flags'], list)
            assert 'fallback_analysis_used' in result['procurement_flags']


class TestAdvancedLLMHandlerFunctionality:
    """Test suite for advanced LLM handler functionality to increase coverage"""

    def test_change_model_openai_config_update(self, mock_openai_provider):
        """Test that OpenAI model changes update user config"""
        mock_openai_provider.change_model.return_value = {
            'success': True,
            'message': 'Model changed successfully',
            'current_model': 'gpt-4'
        }
        
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider), \
             patch('app.config.user_settings.user_settings.update_llm_config') as mock_update:
            handler = LLMHandler()
            handler._provider_type = 'openai'
            
            result = handler.change_model('gpt-4')
            
            assert result['success'] is True
            mock_update.assert_called_once_with({'openai_model': 'gpt-4'})

    def test_get_model_info_success(self, mock_openai_provider):
        """Test get_model_info returns correct information"""
        mock_openai_provider.get_available_models.return_value = [
            {'name': 'gpt-4o', 'description': 'Test model'}
        ]
        mock_openai_provider.get_current_model.return_value = 'gpt-4o'
        mock_openai_provider.check_connection.return_value = True
        
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            
            result = handler.get_model_info()
            
            assert result['name'] == 'gpt-4o'
            assert result['provider'] == 'openai'
            assert result['connection_healthy'] is True
            assert len(result['available_models']) == 1


    def test_generate_with_provider_success(self, mock_openai_provider):
        """Test successful generation with provider"""
        mock_openai_provider._generate_response.return_value = "Generated response"
        
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            
            result = handler._generate_with_provider("test prompt")
            
            assert result == "Generated response"
            mock_openai_provider._generate_response.assert_called_once_with("test prompt")

    def test_generate_with_provider_no_provider(self):
        """Test generation fails when no provider available"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            with pytest.raises(LLMAnalysisError) as exc_info:
                handler._generate_with_provider("test prompt")
            
            assert "No provider available" in str(exc_info.value)

    def test_generate_with_provider_exception(self, mock_openai_provider):
        """Test generation handles provider exceptions"""
        mock_openai_provider._generate_response.side_effect = Exception("Provider failed")
        
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            
            with pytest.raises(LLMAnalysisError) as exc_info:
                handler._generate_with_provider("test prompt")
            
            assert "Provider generation failed" in str(exc_info.value)

    def test_parse_analysis_response_json_cleaning(self):
        """Test JSON response cleaning with code blocks"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            json_response = {
                "explanation": "Test explanation",
                "category": "FINANCIAL",
                "classification": "SIGNIFICANT"
            }
            
            # Test with code block formatting
            response_text = f"```json\n{json.dumps(json_response)}\n```"
            
            result = handler._parse_analysis_response(response_text, "deleted", "inserted")
            
            assert result['explanation'] == "Test explanation"
            assert result['category'] == "FINANCIAL"
            assert result['classification'] == "SIGNIFICANT"

    def test_parse_analysis_response_invalid_required_reviews(self):
        """Test parsing with invalid required_reviews format"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            # Test with string instead of list
            json_response = {
                "explanation": "Test explanation",
                "required_reviews": "FINANCE_APPROVAL",
                "procurement_flags": "test_flag"
            }
            
            result = handler._parse_analysis_response(
                json.dumps(json_response), "deleted", "inserted"
            )
            
            assert isinstance(result['required_reviews'], list)
            assert result['required_reviews'] == ['FINANCE_APPROVAL']
            assert isinstance(result['procurement_flags'], list)
            assert result['procurement_flags'] == ['test_flag']

    def test_fallback_classification_actual_to_placeholder(self):
        """Test fallback classification for actual to placeholder changes"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            result = handler._fallback_classification(
                "Acme Corporation",
                "[COMPANY_NAME]"
            )
            
            assert result == 'SIGNIFICANT'

    def test_fallback_classification_monetary_detection(self):
        """Test fallback classification detects monetary values correctly"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            # Test various monetary formats
            test_cases = [
                ("$1,000", "$2,000"),
                ("£500.50", "£750.25"),
                ("€1000", "€1500"),
                ("¥10,000", "¥15,000"),
                ("1000 USD", "1500 USD"),
                ("500 dollars", "750 dollars")
            ]
            
            for deleted, inserted in test_cases:
                result = handler._fallback_classification(deleted, inserted)
                assert result == 'CRITICAL', f"Failed for {deleted} -> {inserted}"

    def test_fallback_classification_company_names(self):
        """Test fallback classification detects company name changes"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            result = handler._fallback_classification(
                "Acme Corporation Inc",
                "Beta Solutions LLC"
            )
            
            assert result == 'CRITICAL'

    def test_fallback_classification_service_changes(self):
        """Test fallback classification detects service changes"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            result = handler._fallback_classification(
                "software development services",
                "consulting services"
            )
            
            assert result == 'CRITICAL'

    def test_fallback_classification_critical_keywords(self):
        """Test fallback classification detects critical keywords"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            critical_cases = [
                ("no penalty", "penalty clause"),
                ("limited liability", "unlimited liability"),
                ("termination clause", "breach of contract"),
                ("shall comply", "shall not comply")
            ]
            
            for deleted, inserted in critical_cases:
                result = handler._fallback_classification(deleted, inserted)
                assert result == 'CRITICAL', f"Failed for {deleted} -> {inserted}"

    def test_fallback_classification_default(self):
        """Test fallback classification default behavior"""
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=None):
            handler = LLMHandler()
            
            # Test with minimal text
            result = handler._fallback_classification("a", "b")
            
            # Should return some classification (exact value depends on logic)
            assert result in ['CRITICAL', 'SIGNIFICANT', 'INCONSEQUENTIAL']

    def test_analyze_changes_progress_logging(self, mock_openai_provider):
        """Test that analyze_changes logs progress for large batches"""
        mock_response = {
            "explanation": "Test analysis",
            "category": "ADMINISTRATIVE",
            "classification": "INCONSEQUENTIAL"
        }
        
        mock_openai_provider._generate_response.return_value = json.dumps(mock_response)
        
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            
            # Create 15 changes to trigger progress logging
            changes = []
            for i in range(15):
                changes.extend([
                    ('delete', f'old text {i}'),
                    ('insert', f'new text {i}')
                ])
            
            with patch('app.services.llm.handler.logger') as mock_logger:
                results = handler.analyze_changes(changes)
                
                # Should have logged progress at 10 items
                mock_logger.info.assert_any_call("Processed 10/15 changes")
                assert len(results) == 15

    def test_analyze_changes_success(self, mock_openai_provider):
        """Test analyze_changes processes multiple changes successfully"""
        mock_response = {
            "explanation": "Test analysis",
            "category": "ADMINISTRATIVE",
            "classification": "INCONSEQUENTIAL"
        }
        
        mock_openai_provider._generate_response.return_value = json.dumps(mock_response)
        
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            
            changes = [
                ('delete', 'text1'), ('insert', 'text1'),
                ('delete', 'text2'), ('insert', 'text2')
            ]
            
            results = handler.analyze_changes(changes)
            
            # Should have 2 results
            assert len(results) == 2
            # Both should be successful
            for result in results:
                assert result['explanation'] == "Test analysis"
                assert result['classification'] == "INCONSEQUENTIAL"

    def test_get_health_status_exception_handling(self, mock_openai_provider):
        """Test get_health_status handles exceptions"""
        mock_openai_provider.get_health_status.side_effect = Exception("Health check failed")
        
        with patch('app.services.llm.provider_factory.create_llm_provider', return_value=mock_openai_provider):
            handler = LLMHandler()
            
            result = handler.get_health_status()
            
            assert result['connection_healthy'] is False
            assert result['analysis_functional'] is False
            assert result['status'] == 'unhealthy'
            assert 'Health check failed' in result['error']

    def test_backward_compatibility_functions(self):
        """Test backward compatibility functions work correctly"""
        with patch('app.services.llm.handler.LLMHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler.get_change_analysis.return_value = {"test": "result"}
            mock_handler.check_connection.return_value = True
            mock_handler_class.return_value = mock_handler
            
            # Test get_change_analysis function
            from app.services.llm.handler import get_change_analysis
            result = get_change_analysis("deleted", "inserted")
            assert result == {"test": "result"}
            
            # Test test_openai_connection function
            from app.services.llm.handler import test_openai_connection
            result = test_openai_connection()
            assert result is True