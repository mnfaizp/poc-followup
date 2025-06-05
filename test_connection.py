"""
Test script to verify Supabase and Gemini API connections.
Run this before starting the main application to debug connection issues.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_variables():
    """Test if all required environment variables are set."""
    print("🔍 Checking environment variables...")
    
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "GEMINI_API_KEY", "AUTH_USERNAME", "AUTH_PASSWORD"]
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * (len(value) - 10) + value[-10:]}")  # Hide most of the key
        else:
            print(f"❌ {var}: Not found")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file and ensure all variables are set.")
        return False
    
    print("\n✅ All environment variables are set!")
    return True

def test_supabase_connection():
    """Test Supabase connection."""
    print("\n🔍 Testing Supabase connection...")
    
    try:
        from supabase import create_client
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        # Create client
        supabase = create_client(supabase_url, supabase_key)
        
        # Test connection by trying to access a table (this will fail if tables don't exist, but connection works)
        result = supabase.table("prompts").select("count", count="exact").execute()
        
        print("✅ Supabase connection successful!")
        print(f"📊 Prompts table accessible (count: {result.count})")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {str(e)}")
        print("\nPossible solutions:")
        print("1. Check your SUPABASE_URL and SUPABASE_KEY in .env file")
        print("2. Ensure your Supabase project is active")
        print("3. Run the database_schema.sql in your Supabase SQL editor")
        print("4. Check if you have the correct supabase package version")
        return False

def test_gemini_connection():
    """Test Google Gemini API connection."""
    print("\n🔍 Testing Google Gemini API connection...")
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        
        # Test with a simple generation
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, this is a test. Please respond with 'Connection successful!'")
        
        if response.text:
            print("✅ Gemini API connection successful!")
            print(f"🤖 Test response: {response.text[:100]}...")
            return True
        else:
            print("❌ Gemini API responded but with empty content")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API connection failed: {str(e)}")
        print("\nPossible solutions:")
        print("1. Check your GEMINI_API_KEY in .env file")
        print("2. Ensure your API key is valid and has quota")
        print("3. Check your internet connection")
        return False

def main():
    """Run all connection tests."""
    print("🚀 Starting connection tests...\n")
    
    # Test environment variables
    env_ok = test_environment_variables()
    if not env_ok:
        return
    
    # Test Supabase
    supabase_ok = test_supabase_connection()
    
    # Test Gemini
    gemini_ok = test_gemini_connection()
    
    # Summary
    print("\n" + "="*50)
    print("📋 CONNECTION TEST SUMMARY")
    print("="*50)
    print(f"Environment Variables: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"Supabase Connection:   {'✅ PASS' if supabase_ok else '❌ FAIL'}")
    print(f"Gemini API Connection: {'✅ PASS' if gemini_ok else '❌ FAIL'}")
    
    if env_ok and supabase_ok and gemini_ok:
        print("\n🎉 All tests passed! You can now run the main application:")
        print("   streamlit run app.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above before running the main application.")

if __name__ == "__main__":
    main()
