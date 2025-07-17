"""
LLM Provider Architecture for Contract Analyzer
Supports OpenAI with unified interface
"""

import json
import re
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
import requests

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

class BaseLLMProvider(ABC):
    """
    Abstract base class for all LLM providers
    Defines the interface that all providers must implement
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the provider with configuration"""
        self.config = config
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 2)
        self.temperature = config.get('temperature', 0.1)
        self.max_tokens = config.get('max_tokens', 1024)
        
        # Connection state
        self._connection_healthy = None
        self._last_check = 0
        self._check_interval = 30  # seconds
    
    @abstractmethod
    def _generate_response(self, prompt: str) -> str:
        """Generate response from the LLM provider"""
        pass
    
    @abstractmethod
    def check_connection(self) -> bool:
        """Check if the provider is accessible"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of this provider"""
        pass
    
    @abstractmethod
    def get_current_model(self) -> str:
        """Get the currently active model"""
        pass
    
    @abstractmethod
    def change_model(self, new_model: str) -> Dict[str, Any]:
        """Change the active model"""
        pass
    
    @contextmanager
    def _handle_provider_errors(self, operation: str):
        """Context manager for handling provider-specific errors"""
        try:
            yield
        except Exception as e:
            logger.error(f"Provider error during {operation}: {e}")
            raise LLMError(f"Provider error: {e}")
    
    def _retry_with_backoff(self, func, *args, **kwargs):
        """Execute function with exponential backoff retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except (LLMConnectionError, LLMAnalysisError) as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries + 1} attempts failed")
                    break
        
        raise last_exception
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status of the provider"""
        try:
            connection_ok = self.check_connection()
            
            if connection_ok:
                # Test with a simple prompt
                try:
                    test_result = self._generate_response("test")
                    analysis_ok = bool(test_result and test_result.strip())
                except:
                    analysis_ok = False
            else:
                analysis_ok = False
            
            return {
                'provider': self.get_provider_name(),
                'model': self.get_current_model(),
                'connection_healthy': connection_ok,
                'analysis_functional': analysis_ok,
                'last_check': self._last_check,
                'status': 'healthy' if connection_ok and analysis_ok else 'degraded'
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'provider': self.get_provider_name(),
                'model': self.get_current_model(),
                'connection_healthy': False,
                'analysis_functional': False,
                'last_check': self._last_check,
                'status': 'unhealthy',
                'error': str(e)
            }

class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI API provider implementation
    Supports GPT-4o, GPT-4-turbo, GPT-4, GPT-3.5-turbo, and other OpenAI models
    """
    
    # OpenAI model definitions with descriptions
    AVAILABLE_MODELS = {
        'gpt-4o-mini': {
            'name': 'gpt-4o-mini',
            'description': '🚀 FASTEST: Ultra-fast GPT-4-level model. 60% cheaper than gpt-4o. Perfect for batch processing and speed-critical tasks.',
            'context_window': 128000,
            'recommended': True,
            'tier': 'gpt-4-mini',
            'speed': 'ultra-fast',
            'cost': 'ultra-cheap'
        },
        'gpt-4o': {
            'name': 'gpt-4o',
            'description': 'Fastest and cheapest GPT-4-tier model. Multimodal (text, vision, audio input), high quality. Best for most tasks.',
            'context_window': 128000,
            'recommended': True,
            'tier': 'gpt-4'
        },
        'gpt-4-turbo': {
            'name': 'gpt-4-turbo',
            'description': 'GPT-4-based model optimized for performance and cost. Chat-completion only. Slightly slower than gpt-4o.',
            'context_window': 128000,
            'recommended': True,
            'tier': 'gpt-4'
        },
        'gpt-4': {
            'name': 'gpt-4',
            'description': 'Original GPT-4. Slower and more expensive. Mostly deprecated for new apps.',
            'context_window': 8192,
            'recommended': False,
            'tier': 'gpt-4'
        },
        'gpt-3.5-turbo': {
            'name': 'gpt-3.5-turbo',
            'description': 'Lightweight GPT-3.5 model. Cheaper and faster than GPT-4, but lower quality. Still good for many tasks.',
            'context_window': 16385,
            'recommended': True,
            'tier': 'gpt-3.5'
        },
        'gpt-3.5-turbo-16k': {
            'name': 'gpt-3.5-turbo-16k',
            'description': 'Same as gpt-3.5-turbo but with 16k context window. Useful for longer prompts or memory.',
            'context_window': 16385,
            'recommended': False,
            'tier': 'gpt-3.5'
        }
    }
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize OpenAI provider with optimizations"""
        super().__init__(config)
        
        # OpenAI-specific configuration
        self.api_key = config.get('api_key')
        self.model = config.get('model', 'gpt-4o')  # Default to high-quality model
        self.timeout = config.get('timeout', 15)  # ⚡ Reduced timeout for speed
        self.base_url = config.get('base_url', 'https://api.openai.com/v1')
        
        # 🚀 PERFORMANCE OPTIMIZATIONS
        self.max_tokens = config.get('max_tokens', 512)  # ⚡ Reduced for faster responses
        self.temperature = config.get('temperature', 0.1)  # ⚡ Lower for consistency
        
        # Validate API key
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Import OpenAI client with optimizations
        try:
            import openai
            import httpx
            
            # 🚀 CONNECTION POOLING: Create HTTP client with connection pooling
            http_client = httpx.Client(
                timeout=self.timeout,
                limits=httpx.Limits(
                    max_keepalive_connections=20,  # Connection pool size
                    max_connections=100,           # Max total connections
                    keepalive_expiry=30           # Keep connections alive for 30s
                ),
                headers={
                    "User-Agent": "ContractAnalyzer/1.0 (Optimized)",
                    "Connection": "keep-alive"
                }
            )
            
            self.client = openai.OpenAI(
                api_key=self.api_key,
                timeout=self.timeout,
                max_retries=2,  # ⚡ Reduced retries for speed
                http_client=http_client
            )
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai httpx")
        
        logger.info(f"🚀 OpenAI Provider initialized (OPTIMIZED) - Model: {self.model}, Timeout: {self.timeout}s, Connection Pooling: Enabled")
    
    def _generate_response(self, prompt: str) -> str:
        """Generate response using OpenAI API with optimizations"""
        try:
            # ⚡ OPTIMIZATION: Truncate extremely long prompts to save tokens
            max_prompt_length = 8000  # Reasonable limit for batch processing
            if len(prompt) > max_prompt_length:
                prompt = prompt[:max_prompt_length] + "\n\n[TRUNCATED for speed]"
                logger.warning(f"Truncated prompt to {max_prompt_length} characters for speed")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
                # ⚡ OPTIMIZATION: Additional speed settings
                stream=False,  # Disable streaming for batch processing
                frequency_penalty=0.0,  # Reduce processing overhead
                presence_penalty=0.0    # Reduce processing overhead
            )
            
            if not response.choices or not response.choices[0].message:
                raise LLMAnalysisError("Empty or invalid response from OpenAI")
            
            content = response.choices[0].message.content
            
            # ⚡ OPTIMIZATION: Log token usage for monitoring
            if hasattr(response, 'usage') and response.usage:
                logger.debug(f"Tokens used: {response.usage.total_tokens} (prompt: {response.usage.prompt_tokens}, completion: {response.usage.completion_tokens})")
            
            return content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            if "rate limit" in str(e).lower():
                raise LLMConnectionError("OpenAI rate limit exceeded")
            elif "invalid api key" in str(e).lower():
                raise LLMConnectionError("Invalid OpenAI API key")
            elif "model not found" in str(e).lower():
                raise LLMConnectionError(f"Model {self.model} not found")
            elif "timeout" in str(e).lower():
                raise LLMConnectionError(f"Request timed out after {self.timeout}s")
            else:
                raise LLMAnalysisError(f"OpenAI API error: {e}")
    
    def check_connection(self) -> bool:
        """Check if OpenAI API is accessible with caching"""
        current_time = time.time()
        
        # Use cached result if within check interval
        if (self._connection_healthy is not None and 
            current_time - self._last_check < self._check_interval):
            return self._connection_healthy
        
        try:
            # Test connection by listing models
            models = self.client.models.list()
            
            # Check if our model is available
            available_models = [model.id for model in models.data]
            if self.model not in available_models:
                logger.warning(f"Model {self.model} not available. Available models: {available_models[:5]}...")
                self._connection_healthy = False
            else:
                logger.debug(f"OpenAI connection healthy. Model {self.model} available.")
                self._connection_healthy = True
            
            self._last_check = current_time
            return self._connection_healthy
            
        except Exception as e:
            logger.error(f"OpenAI connection check failed: {e}")
            self._connection_healthy = False
            self._last_check = current_time
            return False
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available OpenAI models with descriptions"""
        try:
            model_list = []
            
            for model_key, model_info in self.AVAILABLE_MODELS.items():
                model_data = {
                    'name': model_info['name'],
                    'description': model_info['description'],
                    'context_window': model_info['context_window'],
                    'recommended': model_info['recommended'],
                    'tier': model_info['tier'],
                    'current': model_info['name'] == self.model,
                    'provider': 'openai'
                }
                model_list.append(model_data)
            
            # Sort by recommendation first, then by tier (GPT-4 first), then by name
            model_list.sort(key=lambda x: (not x['recommended'], x['tier'] != 'gpt-4', x['name']))
            return model_list
            
        except Exception as e:
            logger.error(f"Failed to get OpenAI models: {e}")
            return []
    
    def get_provider_name(self) -> str:
        """Get the name of this provider"""
        return "openai"
    
    def get_model_recommendations(self) -> Dict[str, List[str]]:
        """Get model recommendations for different use cases"""
        return {
            'recommended': [model for model, info in self.AVAILABLE_MODELS.items() if info['recommended']],
            'fastest': ['gpt-4o', 'gpt-3.5-turbo'],
            'cheapest': ['gpt-3.5-turbo', 'gpt-4o'],
            'highest_quality': ['gpt-4o', 'gpt-4-turbo', 'gpt-4'],
            'long_context': ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo-16k']
        }
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific model"""
        return self.AVAILABLE_MODELS.get(model_name, {})
    
    def get_current_model(self) -> str:
        """Get the currently active model"""
        return self.model
    
    def change_model(self, new_model: str) -> Dict[str, Any]:
        """Change the active OpenAI model"""
        if not new_model:
            return {
                'success': False,
                'message': 'Model name cannot be empty',
                'current_model': self.model
            }
        
        old_model = self.model
        
        try:
            # Check if new model is available in our curated list
            if new_model not in self.AVAILABLE_MODELS:
                available_names = list(self.AVAILABLE_MODELS.keys())
                return {
                    'success': False,
                    'message': f"Model '{new_model}' not supported. Available: {available_names}",
                    'current_model': old_model
                }
            
            # Test the new model
            try:
                self.model = new_model
                self._connection_healthy = None  # Reset connection state
                self._last_check = 0
                
                # Test with a simple prompt
                test_result = self._generate_response("Test prompt")
                
                if test_result:
                    logger.info(f"OpenAI model changed from '{old_model}' to '{new_model}'")
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
                logger.error(f"OpenAI model change failed: {e}")
                return {
                    'success': False,
                    'message': f"Model change failed: {str(e)}. Reverted to '{old_model}'",
                    'current_model': old_model
                }
                
        except Exception as e:
            logger.error(f"OpenAI model change error: {e}")
            return {
                'success': False,
                'message': f"Model change error: {str(e)}",
                'current_model': self.model
            }

# Ollama provider removed - OpenAI only implementation

def create_llm_provider(provider_type: str, config: Dict[str, Any]) -> BaseLLMProvider:
    """
    Factory function to create LLM providers
    
    Args:
        provider_type: Type of provider (only 'openai' supported)
        config: Configuration dictionary
        
    Returns:
        BaseLLMProvider: Configured provider instance
    """
    if provider_type == 'openai':
        return OpenAIProvider(config)
    else:
        raise ValueError(f"Unknown provider type: {provider_type}. Only 'openai' is supported.") 