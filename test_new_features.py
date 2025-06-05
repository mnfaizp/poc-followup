#!/usr/bin/env python3
"""
Test script for the new multi-user follow-up questions features.
"""
import os
from dotenv import load_dotenv
from database import DatabaseManager
from ai_service import AIService

def test_database_connection():
    """Test database connection and basic operations."""
    print("🔍 Testing database connection...")
    
    try:
        db = DatabaseManager()
        print("✅ Database connection successful!")
        
        # Test basic operations
        prompts = db.get_all_prompts()
        users = db.get_all_users()
        
        print(f"📊 Found {len(prompts)} prompts and {len(users)} users")
        
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_ai_service():
    """Test AI service connection."""
    print("🔍 Testing AI service connection...")
    
    try:
        ai = AIService()
        print("✅ AI service initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ AI service failed: {e}")
        return False

def test_new_models():
    """Test the new data models."""
    print("🔍 Testing new data models...")
    
    from models import User, Experiment, ExperimentCase, CaseResult
    
    try:
        # Test User model
        user = User(name="Test User", email="test@example.com")
        print(f"✅ User model: {user.name}")
        
        # Test Experiment model
        experiment = Experiment(name="Test Experiment", description="Test description", prompt_id=1)
        print(f"✅ Experiment model: {experiment.name}")
        
        # Test ExperimentCase model
        case = ExperimentCase(experiment_id=1, question_id=1, user_id=1, is_selected=True)
        print(f"✅ ExperimentCase model: experiment_id={case.experiment_id}")
        
        print("✅ All new models working correctly!")
        return True
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting tests for new multi-user features...\n")
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "GEMINI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        return
    
    print("✅ Environment variables found")
    
    # Run tests
    tests = [
        test_new_models,
        test_database_connection,
        test_ai_service
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! The new features are ready to use.")
        print("\n📝 Next steps:")
        print("1. Run the Streamlit app: streamlit run app.py")
        print("2. Create a prompt")
        print("3. Add some questions")
        print("4. Create users (or use the 'Create 5 Default Users' button)")
        print("5. Add answers from different users in the 'Manage Cases' page")
        print("6. Create and run experiments")
        print("7. View results")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
