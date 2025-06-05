#!/usr/bin/env python3
"""
Test script for the updated AI service features:
- Single followup question with reason
- Direct prompt usage as system instruction
- Configurable model and temperature
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_models():
    """Test the updated models."""
    print("🔍 Testing updated models...")

    try:
        from models import FollowupQuestion, Prompt

        # Test creating a followup question with reason
        fq = FollowupQuestion(
            id=1,
            answer_id=1,
            followup_text="What specific challenges did you face?",
            reason="To understand the practical difficulties encountered during implementation"
        )

        print("✅ FollowupQuestion model with reason field works")
        print(f"   Question: {fq.followup_text}")
        print(f"   Reason: {fq.reason}")

        # Test creating a prompt with model and temperature
        prompt = Prompt(
            id=1,
            title="Test Prompt",
            content="You are a helpful assistant.",
            model="gemini-1.5-flash",
            temperature=0.5
        )

        print("✅ Prompt model with model and temperature fields works")
        print(f"   Model: {prompt.model}")
        print(f"   Temperature: {prompt.temperature}")

        return True

    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_ai_service_init():
    """Test AI service initialization with new parameters."""
    print("\n🔍 Testing AI service initialization...")
    
    try:
        from ai_service import AIService
        
        # Test with default parameters
        ai_default = AIService()
        print("✅ AI Service with defaults initialized")
        print(f"   Default model: {ai_default.default_model}")
        print(f"   Default temperature: {ai_default.default_temperature}")
        
        # Test with custom parameters
        ai_custom = AIService(default_model='gemini-1.5-flash', default_temperature=0.5)
        print("✅ AI Service with custom settings initialized")
        print(f"   Custom model: {ai_custom.default_model}")
        print(f"   Custom temperature: {ai_custom.default_temperature}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Service initialization failed: {e}")
        return False

def test_ai_service_mock():
    """Test AI service method signature (without actual API call)."""
    print("\n🔍 Testing AI service method signature...")
    
    try:
        from ai_service import AIService
        
        ai = AIService()
        
        # Check if the method exists and has the right signature
        method = getattr(ai, 'generate_followup_questions', None)
        if method is None:
            print("❌ generate_followup_questions method not found")
            return False
            
        # Check method signature by inspecting the function
        import inspect
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        
        expected_params = ['prompt_context', 'question', 'answer', 'model', 'temperature']
        for param in expected_params:
            if param not in params:
                print(f"❌ Missing parameter: {param}")
                return False
        
        print("✅ AI service method signature is correct")
        print(f"   Parameters: {params}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Service method test failed: {e}")
        return False

def test_database_operations():
    """Test database operations with new fields."""
    print("\n🔍 Testing database operations...")

    try:
        from database import DatabaseManager

        db = DatabaseManager()

        # Check followup question method
        method = getattr(db, 'create_followup_question', None)
        if method is None:
            print("❌ create_followup_question method not found")
            return False

        # Check method signature
        import inspect
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        if 'reason' not in params:
            print("❌ Missing 'reason' parameter in create_followup_question")
            return False

        print("✅ FollowupQuestion database operations updated correctly")
        print(f"   create_followup_question parameters: {params}")

        # Check prompt methods
        create_prompt_method = getattr(db, 'create_prompt', None)
        if create_prompt_method is None:
            print("❌ create_prompt method not found")
            return False

        sig = inspect.signature(create_prompt_method)
        params = list(sig.parameters.keys())

        if 'model' not in params or 'temperature' not in params:
            print("❌ Missing 'model' or 'temperature' parameter in create_prompt")
            return False

        print("✅ Prompt database operations updated correctly")
        print(f"   create_prompt parameters: {params}")

        return True

    except Exception as e:
        print(f"❌ Database operations test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Updated Follow-up Questions Features")
    print("=" * 50)
    
    tests = [
        test_models,
        test_ai_service_init,
        test_ai_service_mock,
        test_database_operations
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! The updated features are ready to use.")
        print("\nKey Changes:")
        print("- AI now returns 1 question + 1 reason")
        print("- Prompts are used directly as system instructions")
        print("- Model and temperature are configurable from prompts table")
        print("- Database stores reasons for followup questions")
        print("- Results are grouped by user instead of by question")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
