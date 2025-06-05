#!/usr/bin/env python3
"""
Test script for authentication functionality.
"""

import os
import sys
from dotenv import load_dotenv

def test_auth_environment_variables():
    """Test if authentication environment variables are set."""
    print("🔍 Testing authentication environment variables...")
    
    # Load environment variables
    load_dotenv()
    
    auth_username = os.getenv("AUTH_USERNAME")
    auth_password = os.getenv("AUTH_PASSWORD")
    
    if not auth_username:
        print("❌ AUTH_USERNAME not found in environment variables")
        return False
    
    if not auth_password:
        print("❌ AUTH_PASSWORD not found in environment variables")
        return False
    
    print(f"✅ AUTH_USERNAME: {auth_username}")
    print(f"✅ AUTH_PASSWORD: {'*' * len(auth_password)}")
    
    return True

def test_auth_module():
    """Test the authentication module."""
    print("\n🔍 Testing authentication module...")
    
    try:
        from auth import AuthManager
        
        # Test initialization
        auth_manager = AuthManager()
        print("✅ AuthManager initialized successfully")
        
        # Test with correct credentials
        username = os.getenv("AUTH_USERNAME")
        password = os.getenv("AUTH_PASSWORD")
        
        if auth_manager.check_credentials(username, password):
            print("✅ Credential validation works correctly")
        else:
            print("❌ Credential validation failed")
            return False
        
        # Test with incorrect credentials
        if not auth_manager.check_credentials("wrong", "credentials"):
            print("✅ Incorrect credentials properly rejected")
        else:
            print("❌ Incorrect credentials were accepted")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing authentication module: {str(e)}")
        return False

def test_streamlit_integration():
    """Test if Streamlit integration works."""
    print("\n🔍 Testing Streamlit integration...")
    
    try:
        # Import streamlit to check if it's available
        import streamlit as st
        print("✅ Streamlit is available")
        
        # Try importing the auth functions
        from auth import require_authentication, show_logout_button, show_login_page
        print("✅ Authentication functions imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error testing Streamlit integration: {str(e)}")
        return False

def main():
    """Run all authentication tests."""
    print("🚀 Starting authentication tests...\n")
    
    tests = [
        ("Environment Variables", test_auth_environment_variables),
        ("Authentication Module", test_auth_module),
        ("Streamlit Integration", test_streamlit_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Testing: {test_name}")
        print('='*50)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    print(f"\n{'='*50}")
    print("📋 AUTHENTICATION TEST SUMMARY")
    print('='*50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All authentication tests passed!")
        print("You can now run the application with authentication enabled:")
        print("   streamlit run app.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix the issues above.")
        print("Make sure your .env file contains AUTH_USERNAME and AUTH_PASSWORD.")

if __name__ == "__main__":
    main()
