#!/usr/bin/env python3
"""
Test script for OpenAI model selection functionality
Demonstrates how to use the new model selection features
"""

import sys
import os
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_providers import OpenAIProvider
from config import config

def test_model_selection():
    """Test the OpenAI model selection functionality"""
    
    print("🔧 Testing OpenAI Model Selection")
    print("=" * 50)
    
    # Check if API key is available
    if not config.OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not found in environment")
        print("Please set your API key in .env file")
        return False
    
    try:
        # Initialize OpenAI provider
        provider_config = {
            'api_key': config.OPENAI_API_KEY,
            'model': config.OPENAI_MODEL,
            'timeout': config.OPENAI_TIMEOUT,
            'temperature': config.LLM_TEMPERATURE,
            'max_tokens': config.LLM_MAX_TOKENS
        }
        
        provider = OpenAIProvider(provider_config)
        print(f"✅ OpenAI Provider initialized with model: {provider.get_current_model()}")
        
        # Test available models
        print("\n📋 Available Models:")
        print("-" * 30)
        models = provider.get_available_models()
        
        for model in models:
            status = "⭐ CURRENT" if model['current'] else "✅ RECOMMENDED" if model['recommended'] else "  "
            print(f"{status} {model['name']}")
            print(f"     {model['description']}")
            print(f"     Context: {model['context_window']:,} tokens | Tier: {model['tier']}")
            print()
        
        # Test recommendations
        print("\n🎯 Model Recommendations:")
        print("-" * 30)
        recommendations = provider.get_model_recommendations()
        
        for category, models in recommendations.items():
            print(f"• {category.title()}: {', '.join(models)}")
        
        # Test model info
        print("\n🔍 Model Details:")
        print("-" * 30)
        current_model = provider.get_current_model()
        model_info = provider.get_model_info(current_model)
        
        if model_info:
            print(f"Current Model: {current_model}")
            print(f"Description: {model_info['description']}")
            print(f"Context Window: {model_info['context_window']:,} tokens")
            print(f"Recommended: {'Yes' if model_info['recommended'] else 'No'}")
            print(f"Tier: {model_info['tier']}")
        
        # Test model switching
        print("\n🔄 Testing Model Switch:")
        print("-" * 30)
        
        # Try switching to gpt-3.5-turbo
        if current_model != 'gpt-3.5-turbo':
            print("Switching to gpt-3.5-turbo...")
            result = provider.change_model('gpt-3.5-turbo')
            
            if result['success']:
                print(f"✅ {result['message']}")
                print(f"Previous: {result['previous_model']}")
                print(f"Current: {result['current_model']}")
                
                # Switch back
                switch_back = provider.change_model(current_model)
                if switch_back['success']:
                    print(f"✅ Switched back to {current_model}")
                else:
                    print(f"❌ Failed to switch back: {switch_back['message']}")
            else:
                print(f"❌ Model switch failed: {result['message']}")
        
        # Test invalid model
        print("\n❌ Testing Invalid Model:")
        print("-" * 30)
        invalid_result = provider.change_model('invalid-model')
        print(f"Expected failure: {invalid_result['message']}")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def print_model_selection_guide():
    """Print a guide for choosing the right OpenAI model"""
    
    print("\n📖 OpenAI Model Selection Guide")
    print("=" * 50)
    
    print("🥇 **RECOMMENDED MODELS**")
    print("• gpt-4o - Best overall choice (fast, cheap, high quality)")
    print("• gpt-4-turbo - Good balance of performance and cost")
    print("• gpt-3.5-turbo - Budget-friendly option")
    
    print("\n💰 **COST CONSIDERATIONS**")
    print("• Cheapest: gpt-3.5-turbo → gpt-4o → gpt-4-turbo → gpt-4")
    print("• Most expensive: gpt-4 (mostly deprecated)")
    
    print("\n⚡ **PERFORMANCE**")
    print("• Fastest: gpt-4o → gpt-3.5-turbo → gpt-4-turbo → gpt-4")
    print("• Highest quality: gpt-4o → gpt-4-turbo → gpt-4 → gpt-3.5-turbo")
    
    print("\n📝 **CONTEXT WINDOWS**")
    print("• 128k tokens: gpt-4o, gpt-4-turbo")
    print("• 16k tokens: gpt-3.5-turbo, gpt-3.5-turbo-16k")
    print("• 8k tokens: gpt-4 (legacy)")
    
    print("\n🎯 **USE CASE RECOMMENDATIONS**")
    print("• Contract Analysis: gpt-4o (recommended)")
    print("• Budget-conscious: gpt-3.5-turbo")
    print("• Long documents: gpt-4o or gpt-4-turbo")
    print("• High accuracy needed: gpt-4o")

if __name__ == "__main__":
    print_model_selection_guide()
    test_model_selection() 