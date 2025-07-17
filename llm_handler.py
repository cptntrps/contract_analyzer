"""
Enhanced LLM Handler with robust error handling and retry logic
"""

import ollama
import json
import re
import time
import logging
from typing import Dict, List, Optional, Any
from config import config
import requests
from contextlib import contextmanager
from user_config_manager import user_config
from llm_providers import create_llm_provider

# Configure logging
logger = logging.getLogger(__name__)

class LLMError(Exception):
    """Base exception for LLM-related errors"""
    pass

class LLMConnectionError(LLMError):
    """Exception raised when connection to LLM fails"""
    pass

class LLMAnalysisError(LLMError):
    """Exception raised when LLM analysis fails"""
    pass

class LLMHandler:
    """
    Enhanced LLM Handler with robust error handling and retry logic
    """
    
    def __init__(self):
        """Initialize the LLMHandler with configuration"""
        self._provider = None
        self._provider_type = None
        self._initialize_provider()
        
        logger.info(f"LLM Handler initialized - Provider: {self._provider_type}, Model: {self.get_current_model()}")
    
    def _initialize_provider(self):
        """Initialize the appropriate LLM provider"""
        try:
            # Get configuration from user config manager
            provider_config = user_config.get_llm_config()
            self._provider_type = provider_config.get('provider', 'openai')
            
            # Create provider instance
            self._provider = create_llm_provider(self._provider_type, provider_config)
            
            logger.info(f"LLM Provider initialized: {self._provider_type}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM provider: {e}")
            # Fallback to basic configuration
            self._provider_type = 'openai'
            self._provider = None
    
    def _ensure_provider(self):
        """Ensure provider is initialized, reinitialize if needed"""
        if self._provider is None:
            self._initialize_provider()
        return self._provider is not None
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models from current provider
        
        Returns:
            List of model dictionaries with name, size, and other details
        """
        try:
            if self._ensure_provider():
                return self._provider.get_available_models()
            else:
                logger.warning("No provider available for getting models")
                return []
            
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    def change_model(self, new_model: str) -> Dict[str, Any]:
        """
        Change the current LLM model
        
        Args:
            new_model: Name of the new model to use
            
        Returns:
            Dict with success status and message
        """
        try:
            if not self._ensure_provider():
                return {
                    'success': False,
                    'message': 'No provider available',
                    'current_model': self.get_current_model()
                }
            
            # Use provider's change_model method
            result = self._provider.change_model(new_model)
            
            # If successful and using OpenAI, update user config
            if result.get('success') and self._provider_type == 'openai':
                user_config.update_openai_model(new_model)
            
            return result
            
        except Exception as e:
            logger.error(f"Model change error: {e}")
            return {
                'success': False,
                'message': f"Model change error: {str(e)}",
                'current_model': self.get_current_model()
            }
    
    def get_current_model(self) -> str:
        """Get the currently active model"""
        try:
            if self._ensure_provider():
                return self._provider.get_current_model()
            else:
                # Fallback to user config
                return user_config.get_openai_model()
        except Exception as e:
            logger.error(f"Failed to get current model: {e}")
            return "unknown"
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get detailed information about the current model
        
        Returns:
            Dict with model information
        """
        try:
            available_models = self.get_available_models()
            current_model_info = None
            
            for model in available_models:
                if model['name'] == self.model:
                    current_model_info = model
                    break
            
            return {
                'name': self.model,
                'host': self.host,
                'info': current_model_info,
                'available_models': [m['name'] for m in available_models],
                'connection_healthy': self.check_connection()
            }
            
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {
                'name': self.model,
                'host': self.host,
                'info': None,
                'available_models': [],
                'connection_healthy': False,
                'error': str(e)
            }

    @contextmanager
    def _handle_ollama_errors(self, operation: str):
        """Context manager for handling Ollama errors with logging"""
        try:
            yield
        except ollama.ResponseError as e:
            logger.error(f"Ollama response error during {operation}: {e}")
            if e.status_code == 404:
                raise LLMConnectionError(f"Model {self.model} not found. Please ensure it's installed.")
            elif e.status_code == 503:
                raise LLMConnectionError("Ollama service unavailable. Please check the service status.")
            else:
                raise LLMAnalysisError(f"Ollama error: {e}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error during {operation}: Cannot connect to Ollama")
            raise LLMConnectionError("Cannot connect to Ollama service. Please ensure it's running.")
        except requests.exceptions.Timeout:
            logger.error(f"Timeout error during {operation}: Request timed out")
            raise LLMConnectionError(f"Request timed out after {self.timeout} seconds")
        except Exception as e:
            logger.error(f"Unexpected error during {operation}: {e}")
            raise LLMError(f"Unexpected error: {e}")
    
    def _retry_with_backoff(self, func, *args, **kwargs):
        """Execute function with exponential backoff retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except (LLMConnectionError, LLMAnalysisError) as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries + 1} attempts failed")
                    break
        
        raise last_exception
    
    def check_connection(self) -> bool:
        """
        Check if current provider is accessible
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if self._ensure_provider():
                return self._provider.check_connection()
            else:
                return False
                
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            return False
    
    def _generate_with_provider(self, prompt: str) -> str:
        """
        Generate response using current provider with error handling
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            str: The generated response
        """
        try:
            if self._ensure_provider():
                return self._provider._generate_response(prompt)
            else:
                raise LLMAnalysisError("No provider available")
                
        except Exception as e:
            logger.error(f"Provider generation failed: {e}")
            raise LLMAnalysisError(f"Provider generation failed: {e}")
    
    def _parse_analysis_response(self, response_text: str, deleted_text: str, inserted_text: str) -> Dict[str, Any]:
        """
        Parse LLM response with robust error handling
        
        Args:
            response_text: Raw response from LLM
            deleted_text: Original deleted text
            inserted_text: New inserted text
            
        Returns:
            Dict containing parsed analysis
        """
        try:
            # Extract explanation and classification using regex
            explanation_match = re.search(r'EXPLANATION:\s*(.+?)(?=\n|CLASSIFICATION:|$)', 
                                        response_text, re.IGNORECASE | re.DOTALL)
            classification_match = re.search(r'CLASSIFICATION:\s*(SIGNIFICANT|INCONSEQUENTIAL|CRITICAL)', 
                                           response_text, re.IGNORECASE)
            
            explanation = explanation_match.group(1).strip() if explanation_match else None
            classification = classification_match.group(1).upper() if classification_match else None
            
            # Fallback analysis if parsing fails
            if not explanation or not classification:
                logger.warning("Failed to parse LLM response, using fallback analysis")
                explanation = self._fallback_analysis(deleted_text, inserted_text)
                classification = self._fallback_classification(deleted_text, inserted_text)
            
            # Clean up explanation
            explanation = re.sub(r'\s+', ' ', explanation).strip()
            
            return {
                'explanation': explanation,
                'classification': classification,
                'deleted_text': deleted_text,
                'inserted_text': inserted_text,
                'confidence': 'high' if explanation and classification else 'low'
            }
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return {
                'explanation': self._fallback_analysis(deleted_text, inserted_text),
                'classification': self._fallback_classification(deleted_text, inserted_text),
                'deleted_text': deleted_text,
                'inserted_text': inserted_text,
                'confidence': 'low'
            }
    
    def _fallback_analysis(self, deleted_text: str, inserted_text: str) -> str:
        """
        Provide fallback analysis when LLM fails
        
        Args:
            deleted_text: Original text
            inserted_text: New text
            
        Returns:
            str: Fallback explanation
        """
        if not deleted_text and not inserted_text:
            return "No changes detected"
        elif not deleted_text:
            return f"Added new text: '{inserted_text[:50]}...'"
        elif not inserted_text:
            return f"Removed text: '{deleted_text[:50]}...'"
        else:
            # Determine change type for better explanation
            import re
            
            # Check for placeholder patterns
            placeholder_patterns = [
                r'\[.*?\]', r'INSERT\s+\w+', r'_+', r'\.{3,}', 
                r'TBD|TBA|TO BE DETERMINED', r'PLACEHOLDER|FILL IN',
                r'<.*?>', r'\{.*?\}'
            ]
            
            def is_placeholder(text: str) -> bool:
                text_lower = text.lower().strip()
                for pattern in placeholder_patterns:
                    if re.search(pattern, text_lower, re.IGNORECASE):
                        return True
                placeholder_words = ['placeholder', 'insert', 'enter', 'fill', 'tbd', 'tba']
                return any(word in text_lower for word in placeholder_words)
            
            if is_placeholder(deleted_text) and not is_placeholder(inserted_text):
                return f"Filled placeholder '{deleted_text[:30]}...' with actual content: '{inserted_text[:30]}...'"
            elif not is_placeholder(deleted_text) and not is_placeholder(inserted_text):
                return f"CRITICAL: Changed actual value from '{deleted_text[:30]}...' to '{inserted_text[:30]}...'"
            else:
                return f"Changed text from '{deleted_text[:30]}...' to '{inserted_text[:30]}...'"
    
    def _fallback_classification(self, deleted_text: str, inserted_text: str) -> str:
        """
        Provide fallback classification based on updated heuristics
        
        New Logic:
        - Placeholder → Actual content: INCONSEQUENTIAL
        - Actual content → Different actual content: CRITICAL
        - Service/product changes: CRITICAL
        - Monetary value changes: CRITICAL
        - Company/entity changes: CRITICAL
        
        Args:
            deleted_text: Original text
            inserted_text: New text
            
        Returns:
            str: Classification (SIGNIFICANT, INCONSEQUENTIAL, CRITICAL)
        """
        # Detect placeholder patterns
        placeholder_patterns = [
            r'\[.*?\]',  # [insert name here], [company name], etc.
            r'INSERT\s+\w+',  # INSERT NAME, INSERT COMPANY, etc.
            r'_+',  # ________
            r'\.{3,}',  # ...
            r'TBD|TBA|TO BE DETERMINED|TO BE ADDED',
            r'PLACEHOLDER|FILL IN|ENTER\s+\w+',
            r'<.*?>',  # <company name>, <amount>, etc.
            r'\{.*?\}',  # {company}, {amount}, etc.
        ]
        
        def is_placeholder(text: str) -> bool:
            """Check if text contains placeholder patterns"""
            if not text or not text.strip():
                return True
            
            import re
            text_lower = text.lower().strip()
            
            for pattern in placeholder_patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return True
            
            # Check for generic placeholder words
            placeholder_words = ['placeholder', 'insert', 'enter', 'fill', 'tbd', 'tba', 'xxx', 'yyy', 'zzz']
            if any(word in text_lower for word in placeholder_words):
                return True
                
            return False
        
        # Check if this is a placeholder → actual content change
        if is_placeholder(deleted_text) and not is_placeholder(inserted_text):
            # Special case: service/product placeholders should be reviewed
            service_indicators = ['service', 'product', 'deliverable', 'work', 'scope']
            if any(indicator in deleted_text.lower() for indicator in service_indicators):
                return 'INCONSEQUENTIAL'  # Review but inconsequential at first
            return 'INCONSEQUENTIAL'
        
        # Check if this is actual content → different actual content (CRITICAL)
        if not is_placeholder(deleted_text) and not is_placeholder(inserted_text):
            # This is a value-to-value change - always critical
            return 'CRITICAL'
        
        # Check if this is actual content → placeholder (unusual but significant)
        if not is_placeholder(deleted_text) and is_placeholder(inserted_text):
            return 'SIGNIFICANT'
        
        # Monetary value changes (always critical if both have values)
        import re
        money_pattern = r'[\$£€¥]\s*[\d,]+(?:\.\d{2})?|[\d,]+(?:\.\d{2})?\s*(?:dollars?|USD|EUR|GBP)'
        
        deleted_has_money = re.search(money_pattern, deleted_text, re.IGNORECASE)
        inserted_has_money = re.search(money_pattern, inserted_text, re.IGNORECASE)
        
        if deleted_has_money and inserted_has_money:
            return 'CRITICAL'
        
        # Company/entity changes (look for proper nouns)
        def has_company_names(text: str) -> bool:
            # Look for capitalized words that might be company names
            words = text.split()
            capitalized_words = [w for w in words if w and w[0].isupper() and len(w) > 1]
            return len(capitalized_words) >= 2  # Likely company name if 2+ capitalized words
        
        if has_company_names(deleted_text) and has_company_names(inserted_text):
            return 'CRITICAL'
        
        # Service/product changes (both sides have actual content)
        service_keywords = ['service', 'product', 'deliverable', 'work', 'develop', 'create', 'build', 'provide', 'sell']
        deleted_has_service = any(keyword in deleted_text.lower() for keyword in service_keywords)
        inserted_has_service = any(keyword in inserted_text.lower() for keyword in service_keywords)
        
        if deleted_has_service and inserted_has_service and not is_placeholder(deleted_text) and not is_placeholder(inserted_text):
            return 'CRITICAL'
        
        # Critical keywords (legal, compliance, etc.)
        critical_keywords = [
            'shall not', 'prohibited', 'forbidden', 'violation',
            'penalty', 'damages', 'lawsuit', 'legal action',
            'liability', 'indemnif', 'termination', 'breach'
        ]
        
        combined_text = f"{deleted_text} {inserted_text}".lower()
        if any(keyword in combined_text for keyword in critical_keywords):
            return 'CRITICAL'
        
        # Default to significant for substantial changes
        total_length = len(deleted_text) + len(inserted_text)
        if total_length > 200:
            return 'SIGNIFICANT'
        
        return 'INCONSEQUENTIAL'
    
    def get_change_analysis(self, deleted_text: str, inserted_text: str) -> Dict[str, Any]:
        """
        Analyze a single change with comprehensive error handling
        
        Args:
            deleted_text: The text that was removed
            inserted_text: The text that was added
            
        Returns:
            Dict: Analysis result with explanation and classification
        """
        # Skip analysis for empty changes
        if not deleted_text.strip() and not inserted_text.strip():
            return {
                'explanation': "No changes detected",
                'classification': 'INCONSEQUENTIAL',
                'deleted_text': deleted_text,
                'inserted_text': inserted_text,
                'confidence': 'high'
            }
        
        # Check connection before attempting analysis
        if not self.check_connection():
            logger.warning("LLM not available, using fallback analysis")
            return {
                'explanation': self._fallback_analysis(deleted_text, inserted_text),
                'classification': self._fallback_classification(deleted_text, inserted_text),
                'deleted_text': deleted_text,
                'inserted_text': inserted_text,
                'confidence': 'low'
            }
        
        # Construct the prompt
        prompt = f"""
You are a contract analysis expert. Analyze the following change in a contract document and provide:

1. A one-sentence explanation of what this change means
2. A classification: either "SIGNIFICANT", "INCONSEQUENTIAL", or "CRITICAL"

Deleted text: "{deleted_text}"
Inserted text: "{inserted_text}"

Consider a change CRITICAL if it:
- Removes important obligations or rights
- Adds severe penalties or restrictions
- Changes fundamental contract terms

Consider a change SIGNIFICANT if it:
- Alters payment terms, amounts, or schedules
- Changes project scope, deliverables, or timelines
- Modifies liability, warranty, or indemnification clauses
- Affects termination conditions or contract duration
- Changes key personnel or company information
- Alters intellectual property rights or confidentiality terms

Consider a change INCONSEQUENTIAL if it:
- Fixes typos or formatting
- Changes non-material dates or numbers
- Updates contact information without changing the entity
- Reorganizes text without changing meaning
- Corrects grammar or punctuation

Respond in this exact format:
EXPLANATION: [your one-sentence explanation]
CLASSIFICATION: [CRITICAL, SIGNIFICANT, or INCONSEQUENTIAL]
"""
        
        try:
            # Use retry mechanism for LLM generation
            response_text = self._retry_with_backoff(self._generate_with_provider, prompt)
            return self._parse_analysis_response(response_text, deleted_text, inserted_text)
            
        except Exception as e:
            logger.error(f"LLM analysis failed completely: {e}")
            return {
                'explanation': f"Analysis failed: {self._fallback_analysis(deleted_text, inserted_text)}",
                'classification': self._fallback_classification(deleted_text, inserted_text),
                'deleted_text': deleted_text,
                'inserted_text': inserted_text,
                'confidence': 'low'
            }
    
    def analyze_changes(self, changes: List[tuple]) -> List[Dict[str, Any]]:
        """
        Analyze multiple changes with batching and progress tracking
        
        Args:
            changes: List of change tuples [('operation', 'text'), ...]
            
        Returns:
            List: List of analysis results
        """
        logger.info(f"Analyzing {len(changes)} changes")
        results = []
        
        # Group changes into pairs for analysis
        deleted_texts = []
        inserted_texts = []
        
        for operation, text in changes:
            if operation == 'delete':
                deleted_texts.append(text)
            elif operation == 'insert':
                inserted_texts.append(text)
        
        # Process pairs with progress tracking
        max_pairs = max(len(deleted_texts), len(inserted_texts))
        successful_analyses = 0
        
        for i in range(max_pairs):
            deleted_text = deleted_texts[i] if i < len(deleted_texts) else ""
            inserted_text = inserted_texts[i] if i < len(inserted_texts) else ""
            
            if deleted_text or inserted_text:
                try:
                    result = self.get_change_analysis(deleted_text, inserted_text)
                    results.append(result)
                    
                    if result.get('confidence') == 'high':
                        successful_analyses += 1
                    
                    # Log progress every 10 items
                    if (i + 1) % 10 == 0:
                        logger.info(f"Processed {i + 1}/{max_pairs} changes")
                        
                except Exception as e:
                    logger.error(f"Failed to analyze change {i+1}: {e}")
                    # Continue with next change
                    continue
        
        logger.info(f"Analysis complete: {successful_analyses}/{len(results)} high-confidence results")
        return results
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status of the LLM service
        
        Returns:
            Dict: Health status information
        """
        try:
            if self._ensure_provider():
                return self._provider.get_health_status()
            else:
                return {
                    'connection_healthy': False,
                    'analysis_functional': False,
                    'provider': self._provider_type,
                    'model': self.get_current_model(),
                    'status': 'unhealthy',
                    'error': 'No provider available'
                }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'connection_healthy': False,
                'analysis_functional': False,
                'provider': self._provider_type,
                'model': self.get_current_model(),
                'status': 'unhealthy',
                'error': str(e)
            }

# Backward compatibility functions
def get_change_analysis(deleted_text: str, inserted_text: str) -> Dict[str, Any]:
    """Backward compatibility function"""
    handler = LLMHandler()
    return handler.get_change_analysis(deleted_text, inserted_text)

def test_ollama_connection() -> bool:
    """Backward compatibility function"""
    handler = LLMHandler()
    return handler.check_connection() 