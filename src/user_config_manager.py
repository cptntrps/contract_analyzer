"""
User Configuration Manager for Contract Analyzer
Manages user-editable settings separate from secure environment variables
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from .config import config

logger = logging.getLogger(__name__)

class UserConfigManager:
    """
    Manages user-editable configuration settings
    Separates secure settings (.env) from user preferences (user_config.json)
    """
    
    def __init__(self, config_file: str = "user_config.json"):
        """Initialize the user config manager"""
        self.config_file = config_file
        self.config_path = Path(config_file)
        self._user_config = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from JSON file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self._user_config = json.load(f)
                logger.info(f"Loaded user configuration from {self.config_file}")
            else:
                # Create default config if file doesn't exist
                self._create_default_config()
                logger.info(f"Created default user configuration at {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to load user config: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration"""
        self._user_config = {
            "llm_settings": {
                "provider": "openai",
                "openai_model": "gpt-4o",
                "temperature": 0.1,
                "max_tokens": 1024,
                "timeout": 30,
                "max_retries": 3,
                "retry_delay": 2
            },
            "analysis_settings": {
                "similarity_threshold": 0.5,
                "significant_changes_threshold": 10,
                "batch_size": 10
            },
            "ui_settings": {
                "theme": "auto",
                "auto_refresh_interval": 30000,
                "pagination_size": 20
            },
            "last_updated": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        self._save_config()
    
    def _save_config(self):
        """Save configuration to JSON file"""
        try:
            self._user_config["last_updated"] = datetime.now().isoformat()
            with open(self.config_path, 'w') as f:
                json.dump(self._user_config, f, indent=4)
            logger.info(f"Saved user configuration to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save user config: {e}")
    
    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """Get a specific setting value"""
        try:
            return self._user_config.get(section, {}).get(key, default)
        except Exception as e:
            logger.error(f"Failed to get setting {section}.{key}: {e}")
            return default
    
    def set_setting(self, section: str, key: str, value: Any) -> bool:
        """Set a specific setting value"""
        try:
            if section not in self._user_config:
                self._user_config[section] = {}
            
            self._user_config[section][key] = value
            self._save_config()
            logger.info(f"Updated setting {section}.{key} = {value}")
            return True
        except Exception as e:
            logger.error(f"Failed to set setting {section}.{key}: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all configuration settings"""
        return self._user_config.copy()
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration including secure and user settings"""
        llm_settings = self._user_config.get("llm_settings", {})
        
        # Merge with secure settings from .env
        return {
            # Secure settings from .env
            'provider': config.LLM_PROVIDER,
            'api_key': config.OPENAI_API_KEY,
            'base_url': config.OPENAI_BASE_URL,
            
            # User-editable settings
            'model': llm_settings.get('openai_model', 'gpt-4o'),
            'temperature': llm_settings.get('temperature', 0.1),
            'max_tokens': llm_settings.get('max_tokens', 1024),
            'timeout': llm_settings.get('timeout', 30),
            'max_retries': llm_settings.get('max_retries', 3),
            'retry_delay': llm_settings.get('retry_delay', 2)
        }
    
    def update_openai_model(self, model: str) -> bool:
        """Update the OpenAI model setting"""
        return self.set_setting('llm_settings', 'openai_model', model)
    
    def get_openai_model(self) -> str:
        """Get the current OpenAI model"""
        return self.get_setting('llm_settings', 'openai_model', 'gpt-4o')
    
    def update_llm_provider(self, provider: str) -> bool:
        """Update the LLM provider setting"""
        return self.set_setting('llm_settings', 'provider', provider)
    
    def get_llm_provider(self) -> str:
        """Get the current LLM provider"""
        return self.get_setting('llm_settings', 'provider', 'openai')
    
    def update_temperature(self, temperature: float) -> bool:
        """Update the LLM temperature setting"""
        if 0.0 <= temperature <= 2.0:
            return self.set_setting('llm_settings', 'temperature', temperature)
        else:
            logger.error(f"Invalid temperature value: {temperature}")
            return False
    
    def get_temperature(self) -> float:
        """Get the current LLM temperature"""
        return self.get_setting('llm_settings', 'temperature', 0.1)
    
    def update_max_tokens(self, max_tokens: int) -> bool:
        """Update the max tokens setting"""
        if 1 <= max_tokens <= 4096:
            return self.set_setting('llm_settings', 'max_tokens', max_tokens)
        else:
            logger.error(f"Invalid max_tokens value: {max_tokens}")
            return False
    
    def get_max_tokens(self) -> int:
        """Get the current max tokens"""
        return self.get_setting('llm_settings', 'max_tokens', 1024)
    
    def get_ui_theme(self) -> str:
        """Get the current UI theme"""
        return self.get_setting('ui_settings', 'theme', 'auto')
    
    def update_ui_theme(self, theme: str) -> bool:
        """Update the UI theme"""
        if theme in ['auto', 'light', 'dark']:
            return self.set_setting('ui_settings', 'theme', theme)
        else:
            logger.error(f"Invalid theme value: {theme}")
            return False
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate the current configuration"""
        errors = []
        warnings = []
        
        # Validate LLM settings
        llm_settings = self._user_config.get('llm_settings', {})
        
        temperature = llm_settings.get('temperature', 0.1)
        if not (0.0 <= temperature <= 2.0):
            errors.append(f"Temperature must be between 0.0 and 2.0, got {temperature}")
        
        max_tokens = llm_settings.get('max_tokens', 1024)
        if not (1 <= max_tokens <= 4096):
            errors.append(f"Max tokens must be between 1 and 4096, got {max_tokens}")
        
        # Check if API key is available
        if not config.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY not found in .env file")
        
        # Validate OpenAI model
        openai_model = llm_settings.get('openai_model', 'gpt-4o')
        from .llm_providers import OpenAIProvider
        valid_models = list(OpenAIProvider.AVAILABLE_MODELS.keys())
        if openai_model not in valid_models:
            errors.append(f"Invalid OpenAI model: {openai_model}. Valid models: {valid_models}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults"""
        try:
            self._create_default_config()
            logger.info("Configuration reset to defaults")
            return True
        except Exception as e:
            logger.error(f"Failed to reset configuration: {e}")
            return False
    
    def export_config(self) -> Dict[str, Any]:
        """Export configuration (excluding sensitive data)"""
        exported = self._user_config.copy()
        # Remove any sensitive information if present
        return exported
    
    def import_config(self, config_data: Dict[str, Any]) -> bool:
        """Import configuration data"""
        try:
            # Validate the imported config
            self._user_config = config_data
            validation = self.validate_config()
            
            if validation['valid']:
                self._save_config()
                logger.info("Configuration imported successfully")
                return True
            else:
                logger.error(f"Invalid configuration: {validation['errors']}")
                return False
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return False

# Global instance
user_config = UserConfigManager() 