"""
Enhanced LLM Handler with robust error handling and retry logic
"""

import json
import re
import time
import logging
from typing import Dict, List, Optional, Any
from .config import config
import requests
from contextlib import contextmanager
from .user_config_manager import user_config
from .llm_providers import create_llm_provider

# 🚀 PERFORMANCE OPTIMIZATIONS
import hashlib
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue
import asyncio
from concurrent.futures import ProcessPoolExecutor

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
    Enhanced LLM Handler with robust error handling and OPTIMIZED batch processing
    """
    
    def __init__(self):
        """Initialize the LLMHandler with configuration"""
        self._provider = None
        self._provider_type = None
        self.max_retries = 3
        self.retry_delay = 1
        self.timeout = 15  # ⚡ Reduced timeout for faster responses
        
        # 🚀 BALANCED OPTIMIZATIONS (Fast but Accurate) - Define these FIRST
        self.batch_size = 15  # Process up to 15 changes per API call
        self.use_fast_model = True  # Use gpt-4o-mini for speed
        self.max_workers = 5  # Parallel processing workers
        self.cache_size = 1000  # Cache for analysis results
        self.analysis_cache = {}  # In-memory cache for repeated analyses
        self.cache_lock = threading.Lock()  # Thread-safe cache access
        
        # Balanced mode settings - keep accuracy
        self.ultra_fast_mode = False  # Disable ultra-fast mode
        self.max_changes_to_analyze = 150  # Reasonable limit
        self.skip_similarity_calc = False  # Keep similarity calculation
        
        # NOW initialize provider (after all attributes are defined)
        self._initialize_provider()
        
        logger.info(f"LLM Handler initialized - Provider: {self._provider_type}, Model: {self.get_current_model()}")
    
    def _initialize_provider(self):
        """Initialize the appropriate LLM provider"""
        try:
            # Get configuration from user config manager
            provider_config = user_config.get_llm_config()
            self._provider_type = provider_config.get('provider', 'openai')
            
            # 🚀 BALANCED: Use GPT-4o-mini for speed but keep quality settings
            if self._provider_type == 'openai':
                if self.use_fast_model:
                    provider_config['model'] = 'gpt-4o-mini'  # Fast model
                    provider_config['max_tokens'] = 512  # Reasonable token limit
                    provider_config['timeout'] = 12  # Slightly faster timeout
                    logger.info("BALANCED MODE: Using gpt-4o-mini with quality settings")
                else:
                    provider_config['model'] = 'gpt-4o'  # High quality model
                    provider_config['timeout'] = self.timeout
                    logger.info("Using high-quality model: gpt-4o")
            
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
            current_model = self.get_current_model()
            current_model_info = None
            
            for model in available_models:
                if model['name'] == current_model:
                    current_model_info = model
                    break
            
            return {
                'name': current_model,
                'provider': self._provider_type,
                'info': current_model_info,
                'available_models': [m['name'] for m in available_models],
                'connection_healthy': self.check_connection()
            }
            
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {
                'name': 'unknown',
                'provider': self._provider_type,
                'info': None,
                'available_models': [],
                'connection_healthy': False,
                'error': str(e)
            }

    # _handle_ollama_errors removed - OpenAI only implementation
    
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
        Parse enhanced LLM response with multi-stakeholder support
        
        Args:
            response_text: Raw response from LLM (expected JSON format)
            deleted_text: Original deleted text
            inserted_text: New inserted text
            
        Returns:
            Dict containing parsed analysis with multi-stakeholder data
        """
        try:
            # First try to parse as JSON
            try:
                # Clean response text and extract JSON
                json_text = response_text.strip()
                if json_text.startswith('```json'):
                    json_text = json_text[7:]
                if json_text.endswith('```'):
                    json_text = json_text[:-3]
                json_text = json_text.strip()
                
                parsed_response = json.loads(json_text)
                
                # Validate and normalize the response
                result = {
                    'explanation': parsed_response.get('explanation', 'Change analysis not available'),
                    'category': parsed_response.get('category', 'ADMINISTRATIVE'),
                    'classification': parsed_response.get('classification', 'LOW'),
                    'financial_impact': parsed_response.get('financial_impact', 'NONE'),
                    'required_reviews': parsed_response.get('required_reviews', []),
                    'procurement_flags': parsed_response.get('procurement_flags', []),
                    'review_priority': parsed_response.get('review_priority', 'normal'),
                    'deleted_text': deleted_text,
                    'inserted_text': inserted_text,
                    'confidence': parsed_response.get('confidence', 'medium')
                }
                
                # Ensure required_reviews is a list
                if not isinstance(result['required_reviews'], list):
                    result['required_reviews'] = [result['required_reviews']] if result['required_reviews'] else []
                
                # Ensure procurement_flags is a list
                if not isinstance(result['procurement_flags'], list):
                    result['procurement_flags'] = [result['procurement_flags']] if result['procurement_flags'] else []
                
                return result
                
            except json.JSONDecodeError:
                logger.warning("Response not valid JSON, trying legacy format parsing")
                
                # Fallback to legacy regex parsing for backward compatibility
                explanation_match = re.search(r'EXPLANATION:\s*(.+?)(?=\n|CLASSIFICATION:|$)', 
                                            response_text, re.IGNORECASE | re.DOTALL)
                classification_match = re.search(r'CLASSIFICATION:\s*(SIGNIFICANT|INCONSEQUENTIAL|CRITICAL)', 
                                               response_text, re.IGNORECASE)
                
                explanation = explanation_match.group(1).strip() if explanation_match else None
                classification = classification_match.group(1).upper() if classification_match else None
                
                if explanation and classification:
                    return {
                        'explanation': re.sub(r'\s+', ' ', explanation).strip(),
                        'category': 'ADMINISTRATIVE',
                        'classification': classification,
                        'financial_impact': 'NONE',
                        'required_reviews': ['ROUTINE'] if classification == 'INCONSEQUENTIAL' else ['OPS_REVIEW'],
                        'procurement_flags': [],
                        'review_priority': 'normal',
                        'deleted_text': deleted_text,
                        'inserted_text': inserted_text,
                        'confidence': 'medium'
                    }
            
            # If all parsing fails, use fallback analysis
            logger.warning("Failed to parse LLM response, using enhanced fallback analysis")
            return self._create_fallback_analysis(deleted_text, inserted_text)
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return self._create_fallback_analysis(deleted_text, inserted_text)
    
    def _create_fallback_analysis(self, deleted_text: str, inserted_text: str) -> Dict[str, Any]:
        """Create enhanced fallback analysis with multi-stakeholder logic"""
        explanation = self._fallback_analysis(deleted_text, inserted_text)
        classification = self._fallback_classification(deleted_text, inserted_text)
        
        # Determine required reviews based on content analysis
        required_reviews = []
        if any(keyword in (deleted_text + inserted_text).lower() for keyword in 
               ['price', 'cost', 'payment', 'invoice', 'fee', 'rate', 'budget']):
            required_reviews.append('FINANCE_APPROVAL')
        
        if any(keyword in (deleted_text + inserted_text).lower() for keyword in 
               ['liability', 'indemnif', 'legal', 'law', 'court', 'dispute']):
            required_reviews.append('LEGAL_REVIEW')
        
        if any(keyword in (deleted_text + inserted_text).lower() for keyword in 
               ['sla', 'service level', 'performance', 'delivery', 'timeline']):
            required_reviews.append('OPS_REVIEW')
        
        if not required_reviews:
            required_reviews = ['ROUTINE']
        
        return {
            'explanation': explanation,
            'category': 'ADMINISTRATIVE',
            'classification': classification,
            'financial_impact': 'INDIRECT' if 'FINANCE_APPROVAL' in required_reviews else 'NONE',
            'required_reviews': required_reviews,
            'procurement_flags': ['fallback_analysis_used'],
            'review_priority': 'high' if classification == 'CRITICAL' else 'normal',
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
            return self._create_fallback_analysis(deleted_text, inserted_text)
        
        # Construct the enhanced procurement-focused prompt with multi-stakeholder support
        prompt = f"""
You are a procurement contract analysis expert specializing in vendor agreements, SOWs, and service contracts. 
Analyze the following change and identify ALL stakeholders who need to review it:

CHANGE DETAILS:
Deleted text: "{deleted_text}"
Inserted text: "{inserted_text}"

ANALYSIS REQUIRED:
1. Business Impact Summary (one sentence)
2. Primary Category: FINANCIAL | LEGAL_RISK | OPERATIONAL | SCOPE | COMPLIANCE | ADMINISTRATIVE
3. Risk Level: CRITICAL | HIGH | MEDIUM | LOW | MINIMAL
4. Financial Impact: DIRECT | INDIRECT | NONE
5. Required Reviews (select ALL that apply): ["LEGAL_REVIEW", "FINANCE_APPROVAL", "OPS_REVIEW", "COMPLIANCE_CHECK", "SECURITY_REVIEW", "EXEC_APPROVAL"]

MULTI-STAKEHOLDER EXAMPLES:
- Pricing change with new liability terms → ["FINANCE_APPROVAL", "LEGAL_REVIEW"]
- SLA change affecting security requirements → ["OPS_REVIEW", "SECURITY_REVIEW", "COMPLIANCE_CHECK"]
- Major scope expansion with indemnification changes → ["FINANCE_APPROVAL", "LEGAL_REVIEW", "OPS_REVIEW", "EXEC_APPROVAL"]
- Payment term change with penalty clauses → ["FINANCE_APPROVAL", "LEGAL_REVIEW"]

STAKEHOLDER TRIGGER CRITERIA:

🏛️ LEGAL_REVIEW (if ANY apply):
- Liability, indemnification, or limitation changes
- Termination rights, cure periods, or dispute resolution
- IP ownership, licensing, or confidentiality modifications
- Governing law, jurisdiction, or compliance requirements
- Insurance, force majeure, or risk allocation changes

💰 FINANCE_APPROVAL (if ANY apply):
- Pricing, rates, or cost structure changes
- Payment terms, invoicing, or milestone modifications
- Budget impacts, cost caps, or expense reimbursements
- Currency, tax, or financial penalty changes
- Performance bonds or financial guarantees

⚙️ OPS_REVIEW (if ANY apply):
- Service levels, deliverables, or performance metrics
- Timelines, milestones, or acceptance criteria
- Resource allocation or staffing requirements
- Subcontracting or key personnel changes
- Service delivery or operational process changes

🔒 SECURITY_REVIEW (if ANY apply):
- Data access, storage, or processing requirements
- Security standards, certifications, or audits
- Confidentiality, data protection, or privacy terms
- System access or integration requirements

📋 COMPLIANCE_CHECK (if ANY apply):
- Regulatory requirements or industry standards
- Audit rights, record keeping, or reporting obligations
- Certification or accreditation requirements
- Policy adherence or governance changes

👔 EXEC_APPROVAL (if ANY apply):
- High-value contract changes (>$100K impact)
- Fundamental business relationship changes
- Strategic vendor or partnership modifications
- Major risk assumption or liability expansion

RESPONSE FORMAT (respond with valid JSON only):
{{
  "explanation": "Brief business impact summary",
  "category": "PRIMARY_CATEGORY",
  "classification": "RISK_LEVEL", 
  "financial_impact": "DIRECT|INDIRECT|NONE",
  "required_reviews": ["STAKEHOLDER1", "STAKEHOLDER2"],
  "procurement_flags": ["vendor_performance_impact", "cost_predictability_risk"],
  "confidence": "high|medium|low",
  "review_priority": "urgent|high|normal|low"
}}
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
    
    def _create_optimized_batch_prompt(self, change_pairs: List[tuple]) -> str:
        """
        🚀 OPTIMIZATION: Create efficient batch prompt for multiple changes
        
        Args:
            change_pairs: List of (deleted_text, inserted_text) tuples
            
        Returns:
            str: Optimized batch prompt
        """
        # Build a detailed batch prompt with more context
        changes_text = ""
        for i, (deleted, inserted) in enumerate(change_pairs, 1):
            changes_text += f"CHANGE {i}:\n"
            changes_text += f"  Deleted: \"{deleted[:200]}{'...' if len(deleted) > 200 else ''}\"\n"
            changes_text += f"  Inserted: \"{inserted[:200]}{'...' if len(inserted) > 200 else ''}\"\n\n"
        
        # Balanced prompt with key analysis criteria
        prompt = f"""You are a procurement contract analysis expert. Analyze these contract changes:

{changes_text}

For each change, analyze:
1. Business Impact (one sentence)
2. Category: FINANCIAL | LEGAL_RISK | OPERATIONAL | SCOPE | COMPLIANCE | ADMINISTRATIVE
3. Risk Level: CRITICAL | HIGH | MEDIUM | LOW | MINIMAL
4. Financial Impact: DIRECT | INDIRECT | NONE
5. Required Reviews: ["LEGAL_REVIEW", "FINANCE_APPROVAL", "OPS_REVIEW", "COMPLIANCE_CHECK", "SECURITY_REVIEW", "EXEC_APPROVAL"]

Key Stakeholder Triggers:
- LEGAL_REVIEW: liability, indemnification, termination, IP, disputes, insurance
- FINANCE_APPROVAL: pricing, costs, payments, budgets, penalties, currency
- OPS_REVIEW: service levels, deliverables, timelines, resources, performance
- COMPLIANCE_CHECK: regulations, audits, certifications, policies
- SECURITY_REVIEW: data access, confidentiality, system integration
- EXEC_APPROVAL: high-value changes (>$100K), strategic relationships

JSON Response Format:
[
  {{
    "explanation": "Business impact summary",
    "category": "CATEGORY",
    "classification": "RISK_LEVEL", 
    "financial_impact": "DIRECT|INDIRECT|NONE",
    "required_reviews": ["STAKEHOLDER1", "STAKEHOLDER2"],
    "procurement_flags": ["batch_processed"],
    "confidence": "high|medium|low",
    "review_priority": "urgent|high|normal|low"
  }}
]
"""
        return prompt
    
    def _parse_batch_response(self, response_text: str, change_pairs: List[tuple]) -> List[Dict[str, Any]]:
        """
        Parse batch response from optimized prompt
        
        Args:
            response_text: Response from LLM
            change_pairs: Original change pairs
            
        Returns:
            List of analysis results
        """
        try:
            # Clean and parse JSON response
            json_text = response_text.strip()
            if json_text.startswith('```json'):
                json_text = json_text[7:]
            if json_text.endswith('```'):
                json_text = json_text[:-3]
            json_text = json_text.strip()
            
            parsed_responses = json.loads(json_text)
            
            # Convert to our standard format
            results = []
            for i, response in enumerate(parsed_responses):
                if i < len(change_pairs):
                    deleted_text, inserted_text = change_pairs[i]
                    
                    # Map short response to full format
                    stakeholder_map = {
                        'FINANCE': 'FINANCE_APPROVAL',
                        'LEGAL': 'LEGAL_REVIEW', 
                        'OPS': 'OPS_REVIEW',
                        'SECURITY': 'SECURITY_REVIEW',
                        'COMPLIANCE': 'COMPLIANCE_CHECK',
                        'EXEC': 'EXEC_APPROVAL'
                    }
                    
                    required_reviews = []
                    for stakeholder in response.get('stakeholders', []):
                        mapped = stakeholder_map.get(stakeholder, stakeholder)
                        required_reviews.append(mapped)
                    
                    if not required_reviews:
                        required_reviews = ['ROUTINE']
                    
                    result = {
                        'explanation': response.get('impact', 'Change detected'),
                        'category': response.get('category', 'ADMINISTRATIVE'),
                        'classification': response.get('risk', 'MEDIUM'),
                        'financial_impact': 'DIRECT' if response.get('category') == 'FINANCIAL' else 'NONE',
                        'required_reviews': required_reviews,
                        'procurement_flags': ['batch_processed'],
                        'review_priority': 'high' if response.get('risk') == 'CRITICAL' else 'normal',
                        'deleted_text': deleted_text,
                        'inserted_text': inserted_text,
                        'confidence': 'high'
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to parse batch response: {e}")
            # Fallback to individual analysis
            return [self._create_fallback_analysis(deleted, inserted) for deleted, inserted in change_pairs]
    
    def _cache_key(self, deleted_text: str, inserted_text: str) -> str:
        """
        🚀 CACHING: Generate cache key for analysis result
        
        Args:
            deleted_text: Deleted text
            inserted_text: Inserted text
            
        Returns:
            str: Cache key
        """
        combined_text = f"{deleted_text}||{inserted_text}"
        return hashlib.md5(combined_text.encode()).hexdigest()
    
    def _get_cached_analysis(self, deleted_text: str, inserted_text: str) -> Optional[Dict[str, Any]]:
        """
        🚀 CACHING: Get cached analysis result
        
        Args:
            deleted_text: Deleted text
            inserted_text: Inserted text
            
        Returns:
            Optional[Dict]: Cached analysis result or None
        """
        cache_key = self._cache_key(deleted_text, inserted_text)
        
        with self.cache_lock:
            if cache_key in self.analysis_cache:
                logger.debug(f"✅ Cache hit for analysis: {cache_key[:8]}...")
                return self.analysis_cache[cache_key].copy()
        
        return None
    
    def _cache_analysis(self, deleted_text: str, inserted_text: str, result: Dict[str, Any]) -> None:
        """
        🚀 CACHING: Cache analysis result
        
        Args:
            deleted_text: Deleted text
            inserted_text: Inserted text
            result: Analysis result to cache
        """
        cache_key = self._cache_key(deleted_text, inserted_text)
        
        with self.cache_lock:
            # Limit cache size to prevent memory issues
            if len(self.analysis_cache) >= self.cache_size:
                # Remove oldest entry (simple LRU)
                oldest_key = next(iter(self.analysis_cache))
                del self.analysis_cache[oldest_key]
            
            self.analysis_cache[cache_key] = result.copy()
            logger.debug(f"💾 Cached analysis: {cache_key[:8]}...")
    
    def _analyze_single_change_with_cache(self, deleted_text: str, inserted_text: str) -> Dict[str, Any]:
        """
        🚀 CACHING: Analyze single change with caching
        
        Args:
            deleted_text: Deleted text
            inserted_text: Inserted text
            
        Returns:
            Dict: Analysis result
        """
        # Check cache first
        cached_result = self._get_cached_analysis(deleted_text, inserted_text)
        if cached_result:
            return cached_result
        
        # Perform analysis
        result = self.get_change_analysis(deleted_text, inserted_text)
        
        # Cache result
        self._cache_analysis(deleted_text, inserted_text, result)
        
        return result
    
    def analyze_changes_parallel(self, changes: List[tuple]) -> List[Dict[str, Any]]:
        """
        🚀 PARALLEL PROCESSING: Analyze multiple changes in parallel with caching
        
        Args:
            changes: List of change tuples [('operation', 'text'), ...]
            
        Returns:
            List: List of analysis results
        """
        logger.info(f"🚀 PARALLEL ANALYZING {len(changes)} changes with caching")
        
        # Group changes into pairs for analysis
        deleted_texts = []
        inserted_texts = []
        
        for operation, text in changes:
            if operation == 'delete':
                deleted_texts.append(text)
            elif operation == 'insert':
                inserted_texts.append(text)
        
        # Create change pairs
        max_pairs = max(len(deleted_texts), len(inserted_texts))
        change_pairs = []
        
        for i in range(max_pairs):
            deleted_text = deleted_texts[i] if i < len(deleted_texts) else ""
            inserted_text = inserted_texts[i] if i < len(inserted_texts) else ""
            
            if deleted_text or inserted_text:
                change_pairs.append((deleted_text, inserted_text))
        
        if not change_pairs:
            return []
        
        # 🚀 PARALLEL PROCESSING: Use ThreadPoolExecutor for parallel analysis
        all_results = []
        cache_hits = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_pair = {}
            for deleted_text, inserted_text in change_pairs:
                # Check cache first
                cached_result = self._get_cached_analysis(deleted_text, inserted_text)
                if cached_result:
                    all_results.append(cached_result)
                    cache_hits += 1
                else:
                    # Submit to thread pool
                    future = executor.submit(self._analyze_single_change_with_cache, deleted_text, inserted_text)
                    future_to_pair[future] = (deleted_text, inserted_text)
            
            # Collect results as they complete
            for future in as_completed(future_to_pair):
                try:
                    result = future.result()
                    all_results.append(result)
                except Exception as e:
                    deleted_text, inserted_text = future_to_pair[future]
                    logger.error(f"Parallel analysis failed for change: {e}")
                    # Use fallback analysis
                    fallback_result = self._create_fallback_analysis(deleted_text, inserted_text)
                    all_results.append(fallback_result)
        
        logger.info(f"✅ Parallel analysis complete: {len(all_results)} results processed, {cache_hits} cache hits ({cache_hits/len(change_pairs)*100:.1f}% cache hit rate)")
        return all_results
    
    def analyze_changes_batch(self, changes: List[tuple]) -> List[Dict[str, Any]]:
        """
        🚀 OPTIMIZED: Batch analyze multiple changes with single API calls
        
        Args:
            changes: List of change tuples [('operation', 'text'), ...]
            
        Returns:
            List: List of analysis results
        """
        logger.info(f"🚀 BATCH ANALYZING {len(changes)} changes with optimization")
        
        # Group changes into pairs for analysis
        deleted_texts = []
        inserted_texts = []
        
        for operation, text in changes:
            if operation == 'delete':
                deleted_texts.append(text)
            elif operation == 'insert':
                inserted_texts.append(text)
        
        # Create change pairs
        max_pairs = max(len(deleted_texts), len(inserted_texts))
        change_pairs = []
        
        for i in range(max_pairs):
            deleted_text = deleted_texts[i] if i < len(deleted_texts) else ""
            inserted_text = inserted_texts[i] if i < len(inserted_texts) else ""
            
            if deleted_text or inserted_text:
                change_pairs.append((deleted_text, inserted_text))
        
        if not change_pairs:
            return []
        
        # 🚀 OPTIMIZATION: Check cache first, then batch remaining
        all_results = []
        uncached_pairs = []
        cache_hits = 0
        
        # Check cache for all pairs
        for deleted_text, inserted_text in change_pairs:
            cached_result = self._get_cached_analysis(deleted_text, inserted_text)
            if cached_result:
                all_results.append(cached_result)
                cache_hits += 1
            else:
                uncached_pairs.append((deleted_text, inserted_text))
        
        # Process uncached pairs in batches
        if uncached_pairs:
            total_batches = (len(uncached_pairs) + self.batch_size - 1) // self.batch_size
            
            for batch_idx in range(0, len(uncached_pairs), self.batch_size):
                batch_pairs = uncached_pairs[batch_idx:batch_idx + self.batch_size]
                batch_num = (batch_idx // self.batch_size) + 1
                
                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch_pairs)} changes)")
                
                try:
                    if self.check_connection():
                        # Use batch processing for efficiency
                        batch_prompt = self._create_optimized_batch_prompt(batch_pairs)
                        response_text = self._retry_with_backoff(self._generate_with_provider, batch_prompt)
                        batch_results = self._parse_batch_response(response_text, batch_pairs)
                        
                        # Cache results
                        for i, result in enumerate(batch_results):
                            if i < len(batch_pairs):
                                deleted_text, inserted_text = batch_pairs[i]
                                self._cache_analysis(deleted_text, inserted_text, result)
                        
                        all_results.extend(batch_results)
                    else:
                        # Fallback to individual analysis
                        logger.warning("LLM not available, using fallback analysis")
                        batch_results = [self._create_fallback_analysis(deleted, inserted) for deleted, inserted in batch_pairs]
                        all_results.extend(batch_results)
                    
                except Exception as e:
                    logger.error(f"Batch {batch_num} failed: {e}")
                    # Fallback for this batch
                    batch_results = [self._create_fallback_analysis(deleted, inserted) for deleted, inserted in batch_pairs]
                    all_results.extend(batch_results)
        
        logger.info(f"✅ Batch analysis complete: {len(all_results)} results processed, {cache_hits} cache hits ({cache_hits/len(change_pairs)*100:.1f}% cache hit rate)")
        return all_results

    def analyze_changes_ultra_fast(self, changes: List[tuple]) -> List[Dict[str, Any]]:
        """
        🚀 ULTRA-FAST: Analyze changes with maximum speed optimizations
        """
        logger.info(f"🚀 ULTRA-FAST analyzing {len(changes)} changes")
        
        # Limit changes for speed
        if len(changes) > self.max_changes_to_analyze:
            changes = changes[:self.max_changes_to_analyze]
            logger.info(f"⚡ Limited to {self.max_changes_to_analyze} changes for ultra-fast mode")
        
        # Quick grouped analysis with minimal processing
        if len(changes) <= 10:
            # Very small - use fast fallback
            results = []
            for i in range(0, len(changes), 2):
                deleted = changes[i][1] if i < len(changes) and changes[i][0] == 'delete' else ""
                inserted = changes[i+1][1] if i+1 < len(changes) and changes[i+1][0] == 'insert' else ""
                results.append(self._create_ultra_fast_fallback(deleted[:200], inserted[:200]))
            return results
        
        # For larger sets, use optimized batch with short prompts
        change_pairs = []
        deleted_texts = [c[1] for c in changes if c[0] == 'delete']
        inserted_texts = [c[1] for c in changes if c[0] == 'insert']
        
        max_pairs = max(len(deleted_texts), len(inserted_texts))
        for i in range(min(max_pairs, 25)):  # Limit to 25 pairs max
            deleted = deleted_texts[i][:300] if i < len(deleted_texts) else ""
            inserted = inserted_texts[i][:300] if i < len(inserted_texts) else ""
            if deleted or inserted:
                change_pairs.append((deleted, inserted))
        
        if not change_pairs:
            return []
        
        # Single mega-batch for ultra speed
        try:
            if self.check_connection():
                prompt = f"Contract changes analysis. JSON array only:\n"
                for i, (d, ins) in enumerate(change_pairs[:15], 1):  # Max 15 for speed
                    prompt += f"{i}.DEL:\"{d[:50]}\" ADD:\"{ins[:50]}\"\n"
                prompt += 'Reply: [{"type":"ADMIN","risk":"LOW","desc":"change"}]'
                
                response = self._retry_with_backoff(self._generate_with_provider, prompt)
                return self._parse_ultra_fast_response(response, change_pairs)
            else:
                return [self._create_ultra_fast_fallback(d, ins) for d, ins in change_pairs]
                
        except Exception as e:
            logger.error(f"Ultra-fast failed: {e}")
            return [self._create_ultra_fast_fallback(d, ins) for d, ins in change_pairs]
    
    def _parse_ultra_fast_response(self, response_text: str, change_pairs: List[tuple]) -> List[Dict[str, Any]]:
        """Parse ultra-fast response quickly"""
        try:
            # Extract JSON quickly
            json_text = response_text.strip()
            start = json_text.find('[')
            end = json_text.rfind(']') + 1
            if start >= 0 and end > start:
                json_text = json_text[start:end]
            
            parsed = json.loads(json_text)
            results = []
            
            for i, resp in enumerate(parsed):
                if i < len(change_pairs):
                    d, ins = change_pairs[i]
                    results.append({
                        'explanation': resp.get('desc', 'Change detected')[:100],
                        'category': resp.get('type', 'ADMINISTRATIVE'),
                        'classification': resp.get('risk', 'LOW'),
                        'financial_impact': 'NONE',
                        'required_reviews': ['ROUTINE'],
                        'procurement_flags': ['ultra_fast'],
                        'review_priority': 'normal',
                        'deleted_text': d,
                        'inserted_text': ins,
                        'confidence': 'medium'
                    })
            return results
            
        except:
            return [self._create_ultra_fast_fallback(d, ins) for d, ins in change_pairs]
    
    def _create_ultra_fast_fallback(self, deleted_text: str, inserted_text: str) -> Dict[str, Any]:
        """Create ultra-fast fallback analysis"""
        return {
            'explanation': f"Change: '{deleted_text[:30]}...' → '{inserted_text[:30]}...'",
            'category': 'ADMINISTRATIVE',
            'classification': 'INCONSEQUENTIAL',
            'financial_impact': 'NONE',
            'required_reviews': ['ROUTINE'],
            'procurement_flags': ['ultra_fast_fallback'],
            'review_priority': 'normal',
            'deleted_text': deleted_text,
            'inserted_text': inserted_text,
            'confidence': 'medium'
        }

    def analyze_changes(self, changes: List[tuple]) -> List[Dict[str, Any]]:
        """
        🚀 BALANCED: Analyze multiple changes with optimal speed/accuracy balance
        
        Args:
            changes: List of change tuples [('operation', 'text'), ...]
            
        Returns:
            List: List of analysis results
        """
        # Use balanced strategy based on number of changes
        if len(changes) <= 15:
            # For small batches, use parallel processing for better cache utilization
            return self.analyze_changes_parallel(changes)
        else:
            # For larger batches, use batch processing for API efficiency
            return self.analyze_changes_batch(changes)
    
    def analyze_changes_legacy(self, changes: List[tuple]) -> List[Dict[str, Any]]:
        """
        LEGACY: Original individual analysis method (kept for fallback)
        
        Args:
            changes: List of change tuples [('operation', 'text'), ...]
            
        Returns:
            List: List of analysis results
        """
        logger.info(f"Analyzing {len(changes)} changes individually (legacy mode)")
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
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        🚀 PERFORMANCE: Get performance statistics
        
        Returns:
            Dict: Performance statistics
        """
        with self.cache_lock:
            cache_size = len(self.analysis_cache)
        
        return {
            'cache_size': cache_size,
            'cache_limit': self.cache_size,
            'cache_utilization': f"{cache_size/self.cache_size*100:.1f}%",
            'max_workers': self.max_workers,
            'batch_size': self.batch_size,
            'optimization_enabled': True
        }
    
    def clear_cache(self) -> Dict[str, Any]:
        """
        🚀 PERFORMANCE: Clear analysis cache
        
        Returns:
            Dict: Cache clear status
        """
        with self.cache_lock:
            cache_size = len(self.analysis_cache)
            self.analysis_cache.clear()
        
        logger.info(f"✅ Cache cleared: {cache_size} entries removed")
        return {
            'success': True,
            'cleared_entries': cache_size,
            'message': f"Cache cleared successfully: {cache_size} entries removed"
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status of the LLM service
        
        Returns:
            Dict: Health status information
        """
        try:
            if self._ensure_provider():
                health_status = self._provider.get_health_status()
                # Add performance stats
                health_status['performance'] = self.get_performance_stats()
                return health_status
            else:
                return {
                    'connection_healthy': False,
                    'analysis_functional': False,
                    'provider': self._provider_type,
                    'model': self.get_current_model(),
                    'status': 'unhealthy',
                    'error': 'No provider available',
                    'performance': self.get_performance_stats()
                }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'connection_healthy': False,
                'analysis_functional': False,
                'provider': self._provider_type,
                'model': self.get_current_model(),
                'status': 'unhealthy',
                'error': str(e),
                'performance': self.get_performance_stats()
            }

# Backward compatibility functions
def get_change_analysis(deleted_text: str, inserted_text: str) -> Dict[str, Any]:
    """Backward compatibility function"""
    handler = LLMHandler()
    return handler.get_change_analysis(deleted_text, inserted_text)

def test_openai_connection() -> bool:
    """Test OpenAI connection"""
    handler = LLMHandler()
    return handler.check_connection() 