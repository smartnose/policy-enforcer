#!/usr/bin/env python3
"""
Test the main CLI without requiring real OpenAI API key.
"""

import os
import sys
from unittest.mock import patch, MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cli_setup():
    """Test the CLI setup without OpenAI."""
    print("🧪 Testing CLI Setup...")
    
    # Mock the Google client
    with patch('google.generativeai') as mock_google:
        # Set fake API key
        os.environ['GOOGLE_API_KEY'] = 'test-key-123'
        
        # Import after setting the env var
        from policy_enforcer.agents import create_agent
        
        # Mock the LLM to avoid actual API calls
        with patch('langchain_google_genai.ChatGoogleGenerativeAI') as mock_llm:
            mock_llm.return_value = MagicMock()
            
            try:
                agent = create_agent()
                print("✅ Agent created successfully!")
                
                # Test state and rules access
                state_summary = agent.show_state()
                print(f"✅ State access works: {len(state_summary)} characters")
                
                rules_summary = agent.show_rules()
                print(f"✅ Rules access works: {len(rules_summary)} characters")
                
                # Test reset
                agent.reset()
                print("✅ Reset functionality works!")
                
                return True
                
            except Exception as e:
                print(f"❌ Agent creation failed: {e}")
                return False

def main():
    """Run CLI tests."""
    print("🚀 Testing Policy Enforcer CLI Components...\n")
    
    success = test_cli_setup()
    
    if success:
        print("\n🎉 All CLI tests passed!")
        print("\nThe Policy Enforcer is ready for use!")
        print("\nNext steps:")
        print("1. Get a Google API key from https://makersuite.google.com/app/apikey")
        print("2. Copy .env.example to .env and add your API key")
        print("3. Run: python main.py")
        print("4. Or run the demo without API: python demo.py")
    else:
        print("\n❌ CLI tests failed.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
