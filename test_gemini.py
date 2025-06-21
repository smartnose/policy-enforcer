#!/usr/bin/env python3
"""
Test Gemini integration without requiring real API key.
"""

import os
import sys
from unittest.mock import patch, MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gemini_integration():
    """Test that the agent can be created with Gemini."""
    print("🧪 Testing Gemini Integration...")
    
    # Set fake API key
    os.environ['GOOGLE_API_KEY'] = 'test-gemini-key-123'
    
    try:
        # Mock the Gemini client to avoid actual API calls
        with patch('langchain_google_genai.ChatGoogleGenerativeAI') as mock_llm:
            mock_instance = MagicMock()
            mock_llm.return_value = mock_instance
            
            # Import and create agent
            from policy_enforcer.agents import create_agent
            
            agent = create_agent()
            
            # Verify the agent was created with correct model
            assert agent.model_name == "gemini-1.5-flash"
            assert agent.temperature == 0.1
            
            # Verify the LLM was created with correct parameters
            mock_llm.assert_called_once_with(model="gemini-1.5-flash", temperature=0.1)
            
            print("✅ Agent created with Gemini 1.5 Flash")
            print(f"✅ Model name: {agent.model_name}")
            print(f"✅ Temperature: {agent.temperature}")
            
            # Test agent methods
            state_summary = agent.show_state()
            rules_summary = agent.show_rules()
            
            print(f"✅ State access works: {len(state_summary)} chars")
            print(f"✅ Rules access works: {len(rules_summary)} chars")
            
            # Test reset
            agent.reset()
            print("✅ Reset functionality works")
            
            return True
            
    except Exception as e:
        print(f"❌ Gemini integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run Gemini integration test."""
    print("🚀 Testing Policy Enforcer with Gemini 1.5 Flash...\n")
    
    success = test_gemini_integration()
    
    if success:
        print("\n🎉 Gemini integration test passed!")
        print("\n✨ The Policy Enforcer is now powered by Google's Gemini 1.5 Flash!")
        print("\nNext steps:")
        print("1. Get a Google API key from https://makersuite.google.com/app/apikey")
        print("2. Copy .env.example to .env and add your API key")
        print("3. Run: python main.py")
        print("4. Or run the demo without API: python demo.py")
    else:
        print("\n❌ Gemini integration test failed.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
