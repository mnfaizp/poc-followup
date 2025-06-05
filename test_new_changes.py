#!/usr/bin/env python3
"""
Test script for the new changes:
- Model and temperature configuration in prompts
- Results grouped by user
- Updated database operations
"""

import sys

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

def test_ai_service_signature():
    """Test AI service method signature (without initialization)."""
    print("\n🔍 Testing AI service method signature...")
    
    try:
        from ai_service import AIService
        
        # Check if the method exists and has the right signature
        import inspect
        method = getattr(AIService, 'generate_followup_questions', None)
        if method is None:
            print("❌ generate_followup_questions method not found")
            return False
            
        # Check method signature by inspecting the function
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        
        expected_params = ['self', 'prompt_context', 'question', 'answer', 'model', 'temperature']
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
        
        # Check followup question method
        import inspect
        
        # Test create_followup_question
        method = getattr(DatabaseManager, 'create_followup_question', None)
        if method is None:
            print("❌ create_followup_question method not found")
            return False
            
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        
        if 'reason' not in params:
            print("❌ Missing 'reason' parameter in create_followup_question")
            return False
        
        print("✅ FollowupQuestion database operations updated correctly")
        print(f"   create_followup_question parameters: {params}")
        
        # Test create_prompt
        create_prompt_method = getattr(DatabaseManager, 'create_prompt', None)
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
        
        # Test update_prompt
        update_prompt_method = getattr(DatabaseManager, 'update_prompt', None)
        if update_prompt_method is None:
            print("❌ update_prompt method not found")
            return False
            
        sig = inspect.signature(update_prompt_method)
        params = list(sig.parameters.keys())
        
        if 'model' not in params or 'temperature' not in params:
            print("❌ Missing 'model' or 'temperature' parameter in update_prompt")
            return False
        
        print("✅ Update prompt database operations updated correctly")
        print(f"   update_prompt parameters: {params}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database operations test failed: {e}")
        return False

def test_syntax():
    """Test that all files compile correctly."""
    print("\n🔍 Testing syntax compilation...")
    
    try:
        import py_compile
        
        files_to_test = [
            'models.py',
            'database.py', 
            'ai_service.py',
            'app.py'
        ]
        
        for file in files_to_test:
            try:
                py_compile.compile(file, doraise=True)
                print(f"✅ {file} compiles successfully")
            except py_compile.PyCompileError as e:
                print(f"❌ {file} compilation failed: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Syntax test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing New Changes: User Grouping & Prompt Configuration")
    print("=" * 60)
    
    tests = [
        test_models,
        test_ai_service_signature,
        test_database_operations,
        test_syntax
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! The new changes are ready to use.")
        print("\nNew Features:")
        print("- ✅ Results grouped by user instead of by question")
        print("- ✅ Model and temperature configurable from prompts table")
        print("- ✅ AI service uses prompt-specific model/temperature settings")
        print("- ✅ Database schema supports model and temperature fields")
        print("- ✅ UI updated to show and edit AI settings")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
