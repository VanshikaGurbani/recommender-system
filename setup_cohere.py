#!/usr/bin/env python3
"""
Setup script for Cohere API key configuration
"""

import os
import sys
from pathlib import Path

def setup_cohere_api():
    """Setup Cohere API key"""
    print("🔑 Cohere API Key Setup")
    print("=" * 50)
    
    # Check if API key is already set
    current_key = os.getenv('COHERE_API_KEY')
    if current_key and current_key != "your_cohere_api_key_here":
        print(f"✅ Cohere API key is already set: {current_key[:10]}...")
        return True
    
    print("To use the LLM-powered search features, you need a Cohere API key.")
    print("Get your free API key at: https://dashboard.cohere.ai/")
    print()
    
    # Get API key from user
    api_key = input("Enter your Cohere API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. LLM features will not work.")
        return False
    
    # Set environment variable
    os.environ['COHERE_API_KEY'] = api_key
    
    # Create .env file
    env_file = Path('.env')
    with open(env_file, 'w') as f:
        f.write(f"COHERE_API_KEY={api_key}\n")
    
    print("✅ Cohere API key saved to .env file")
    print("✅ Environment variable set for current session")
    print()
    print("🚀 You can now use the LLM-powered search features!")
    print("Try queries like:")
    print("- 'movies like inception'")
    print("- 'romantic comedy from the 90s'")
    print("- 'thriller movies with strong female leads'")
    
    return True

if __name__ == "__main__":
    setup_cohere_api()
