#!/usr/bin/env python3
"""
Interactive OpenAI Model Selection Tool
Helps users choose the right OpenAI model for their contract analysis needs
"""

import os
import sys
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_providers import OpenAIProvider
from config import config

def print_welcome():
    """Print welcome message and instructions"""
    print("🤖 OpenAI Model Selection Tool")
    print("=" * 50)
    print("This tool helps you choose the right OpenAI model for contract analysis.")
    print("Each model has different strengths, costs, and performance characteristics.")
    print()

def show_model_options():
    """Display all available models with their details"""
    print("📋 Available OpenAI Models:")
    print("-" * 50)
    
    # Get model information
    provider_config = {
        'api_key': 'dummy',  # Just for getting model info
        'model': 'gpt-4o',
        'timeout': 30,
        'temperature': 0.1,
        'max_tokens': 1024
    }
    
    # Create provider instance (won't actually connect without real API key)
    try:
        provider = OpenAIProvider(provider_config)
    except:
        # If API key is missing, we can still show the model info
        class MockProvider:
            AVAILABLE_MODELS = OpenAIProvider.AVAILABLE_MODELS
            
            def get_available_models(self):
                models = []
                for model_key, model_info in self.AVAILABLE_MODELS.items():
                    models.append({
                        'name': model_info['name'],
                        'description': model_info['description'],
                        'context_window': model_info['context_window'],
                        'recommended': model_info['recommended'],
                        'tier': model_info['tier'],
                        'current': False,
                        'provider': 'openai'
                    })
                return models
        
        provider = MockProvider()
    
    models = provider.get_available_models()
    
    for i, model in enumerate(models, 1):
        status = "⭐ RECOMMENDED" if model['recommended'] else "  "
        print(f"{i}. {status} {model['name']}")
        print(f"   {model['description']}")
        print(f"   Context: {model['context_window']:,} tokens | Tier: {model['tier']}")
        print()

def get_user_preferences():
    """Get user preferences to recommend the best model"""
    print("🎯 Let's find the best model for your needs!")
    print("-" * 50)
    
    preferences = {}
    
    # Priority preference
    print("1. What's most important to you?")
    print("   a) Speed (fastest responses)")
    print("   b) Cost (cheapest option)")
    print("   c) Quality (highest accuracy)")
    print("   d) Balance (good mix of all)")
    
    priority = input("Choose (a/b/c/d): ").lower().strip()
    preferences['priority'] = priority
    
    # Document length
    print("\n2. How long are your typical contracts?")
    print("   a) Short (1-5 pages)")
    print("   b) Medium (5-20 pages)")
    print("   c) Long (20+ pages)")
    
    length = input("Choose (a/b/c): ").lower().strip()
    preferences['length'] = length
    
    # Budget concern
    print("\n3. How concerned are you about costs?")
    print("   a) Very concerned (minimize costs)")
    print("   b) Somewhat concerned (balance cost and quality)")
    print("   c) Not concerned (quality is priority)")
    
    budget = input("Choose (a/b/c): ").lower().strip()
    preferences['budget'] = budget
    
    return preferences

def recommend_model(preferences: Dict[str, str]) -> str:
    """Recommend a model based on user preferences"""
    
    # Priority-based recommendations
    if preferences['priority'] == 'a':  # Speed
        if preferences['budget'] == 'a':  # Budget-conscious
            return 'gpt-3.5-turbo'
        else:
            return 'gpt-4o'
    
    elif preferences['priority'] == 'b':  # Cost
        return 'gpt-3.5-turbo'
    
    elif preferences['priority'] == 'c':  # Quality
        if preferences['length'] == 'c':  # Long documents
            return 'gpt-4o'
        else:
            return 'gpt-4-turbo'
    
    else:  # Balance
        if preferences['budget'] == 'a':  # Budget-conscious
            return 'gpt-3.5-turbo'
        else:
            return 'gpt-4o'

def show_recommendation(model_name: str, preferences: Dict[str, str]):
    """Show the recommended model with explanation"""
    
    # Get model info
    provider_config = {
        'api_key': 'dummy',
        'model': model_name,
        'timeout': 30,
        'temperature': 0.1,
        'max_tokens': 1024
    }
    
    try:
        provider = OpenAIProvider(provider_config)
        model_info = provider.get_model_info(model_name)
    except:
        # Fallback to static info
        model_info = OpenAIProvider.AVAILABLE_MODELS.get(model_name, {})
    
    print(f"\n🎉 Recommended Model: {model_name}")
    print("=" * 50)
    
    if model_info:
        print(f"Description: {model_info['description']}")
        print(f"Context Window: {model_info['context_window']:,} tokens")
        print(f"Tier: {model_info['tier']}")
        print(f"Recommended: {'Yes' if model_info['recommended'] else 'No'}")
    
    print(f"\n📝 Why this model?")
    
    # Explain the recommendation
    if model_name == 'gpt-4o':
        print("• Best overall choice for contract analysis")
        print("• Fast, cost-effective, and high quality")
        print("• Large context window for long documents")
        print("• Multimodal capabilities (future-proof)")
    
    elif model_name == 'gpt-4-turbo':
        print("• Good balance of performance and cost")
        print("• High quality analysis")
        print("• Large context window")
        print("• Optimized for performance")
    
    elif model_name == 'gpt-3.5-turbo':
        print("• Most cost-effective option")
        print("• Still provides good quality analysis")
        print("• Fast response times")
        print("• Good for simpler contract analysis tasks")
    
    print(f"\n💡 To use this model, update your .env file:")
    print(f"   OPENAI_MODEL={model_name}")

def update_env_file(model_name: str):
    """Offer to update the .env file with the selected model"""
    
    response = input(f"\n🔧 Would you like to update your .env file to use {model_name}? (y/n): ").lower().strip()
    
    if response == 'y':
        env_path = '.env'
        
        if os.path.exists(env_path):
            # Read existing .env file
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            # Update or add OPENAI_MODEL line
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('OPENAI_MODEL='):
                    lines[i] = f'OPENAI_MODEL={model_name}\n'
                    updated = True
                    break
            
            if not updated:
                lines.append(f'OPENAI_MODEL={model_name}\n')
            
            # Write updated file
            with open(env_path, 'w') as f:
                f.writelines(lines)
            
            print(f"✅ Updated .env file with OPENAI_MODEL={model_name}")
        else:
            print("❌ .env file not found. Please create one first.")
    else:
        print("📝 Remember to manually update your .env file when ready.")

def main():
    """Main function to run the interactive model selection"""
    
    print_welcome()
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Show all available models")
        print("2. Get personalized recommendation")
        print("3. Exit")
        
        choice = input("\nChoose (1/2/3): ").strip()
        
        if choice == '1':
            show_model_options()
        
        elif choice == '2':
            preferences = get_user_preferences()
            recommended_model = recommend_model(preferences)
            show_recommendation(recommended_model, preferences)
            update_env_file(recommended_model)
        
        elif choice == '3':
            print("\n👋 Happy analyzing! Remember to update your .env file with your chosen model.")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 