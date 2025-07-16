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
        self.host = config.OLLAMA_HOST
        self.model = config.OLLAMA_MODEL
        self.timeout = config.OLLAMA_TIMEOUT
        self.max_retries = config.OLLAMA_MAX_RETRIES
        self.retry_delay = config.OLLAMA_RETRY_DELAY
        self.temperature = config.LLM_TEMPERATURE
        self.top_p = config.LLM_TOP_P
        self.max_tokens = config.LLM_MAX_TOKENS
        
        # Connection state
        self._connection_healthy = None
        self._last_check = 0
        self._check_interval = 30  # seconds
        
        logger.info(f"LLM Handler initialized - Host: {self.host}, Model: {self.model}")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models from Ollama
        
        Returns:
            List of model dictionaries with name, size, and other details
        """
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            response.raise_for_status()
            
            models_data = response.json()
            models = []
            
            for model in models_data.get('models', []):
                model_info = {
                    'name': model.get('name', ''),
                    'size': model.get('size', 0),
                    'digest': model.get('digest', ''),
                    'modified_at': model.get('modified_at', ''),
                    'details': model.get('details', {}),
                    'current': model.get('name', '') == self.model
                }
                models.append(model_info)
            
            return models
            
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
            # Validate model exists
            available_models = self.get_available_models()
            model_names = [m['name'] for m in available_models]
            
            if new_model not in model_names:
                return {
                    'success': False,
                    'message': f"Model '{new_model}' not available. Available models: {model_names}",
                    'current_model': self.model
                }
            
            # Test the new model with a simple prompt
            old_model = self.model
            self.model = new_model
            
            try:
                # Reset connection state to force recheck
                self._connection_healthy = None
                self._last_check = 0
                
                # Test with a simple prompt
                test_result = self._generate_with_ollama("Test prompt")
                
                if test_result:
                    logger.info(f"Model changed from '{old_model}' to '{new_model}'")
                    return {
                        'success': True,
                        'message': f"Model changed to '{new_model}' successfully",
                        'previous_model': old_model,
                        'current_model': new_model
                    }
                else:
                    # Revert to old model if test failed
                    self.model = old_model
                    return {
                        'success': False,
                        'message': f"Model '{new_model}' failed test. Reverted to '{old_model}'",
                        'current_model': old_model
                    }
                    
            except Exception as e:
                # Revert to old model on error
                self.model = old_model
                logger.error(f"Model change failed: {e}")
                return {
                    'success': False,
                    'message': f"Model change failed: {str(e)}. Reverted to '{old_model}'",
                    'current_model': old_model
                }
                
        except Exception as e:
            logger.error(f"Model change error: {e}")
            return {
                'success': False,
                'message': f"Model change error: {str(e)}",
                'current_model': self.model
            }
    
    def get_current_model(self) -> str:
        """Get the currently active model"""
        return self.model
    
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
        Check if Ollama is running and accessible with caching
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        current_time = time.time()
        
        # Use cached result if within check interval
        if (self._connection_healthy is not None and 
            current_time - self._last_check < self._check_interval):
            return self._connection_healthy
        
        try:
            with self._handle_ollama_errors("connection check"):
                response = requests.get(f"{self.host}/api/tags", timeout=5)
                response.raise_for_status()
                
                models = response.json()
                available_models = [m['name'] for m in models.get('models', [])]
                
                if self.model not in available_models:
                    logger.warning(f"Model {self.model} not available. Available: {available_models}")
                    self._connection_healthy = False
                else:
                    logger.debug(f"Connection healthy. Model {self.model} available.")
                    self._connection_healthy = True
                
                self._last_check = current_time
                return self._connection_healthy
                
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            self._connection_healthy = False
            self._last_check = current_time
            return False
    
    def _generate_with_ollama(self, prompt: str) -> str:
        """
        Generate response using Ollama with error handling
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            str: The generated response
        """
        with self._handle_ollama_errors("text generation"):
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': self.temperature,
                    'top_p': self.top_p,
                    'num_predict': self.max_tokens
                }
            )
            
            if not response or 'response' not in response:
                raise LLMAnalysisError("Empty or invalid response from Ollama")
            
            return response['response']
    
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
            response_text = self._retry_with_backoff(self._generate_with_ollama, prompt)
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
            connection_ok = self.check_connection()
            
            if connection_ok:
                # Test with a simple prompt
                test_result = self.get_change_analysis("test", "test")
                analysis_ok = test_result.get('confidence') == 'high'
            else:
                analysis_ok = False
            
            return {
                'connection_healthy': connection_ok,
                'analysis_functional': analysis_ok,
                'host': self.host,
                'model': self.model,
                'last_check': self._last_check,
                'status': 'healthy' if connection_ok and analysis_ok else 'degraded'
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'connection_healthy': False,
                'analysis_functional': False,
                'host': self.host,
                'model': self.model,
                'last_check': self._last_check,
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