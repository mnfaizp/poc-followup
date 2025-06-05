"""
Authentication module for the Follow-up Questions Manager application.
Provides simple username/password authentication using environment variables.
"""
import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AuthManager:
    """Handles authentication for the application."""
    
    def __init__(self):
        """Initialize authentication manager."""
        self.username = os.getenv("AUTH_USERNAME")
        self.password = os.getenv("AUTH_PASSWORD")
        
        if not self.username or not self.password:
            st.error("Authentication credentials not found in environment variables.")
            st.info("Please set AUTH_USERNAME and AUTH_PASSWORD in your .env file.")
            st.stop()
    
    def check_credentials(self, username: str, password: str) -> bool:
        """
        Check if provided credentials match the configured ones.
        
        Args:
            username: Username to check
            password: Password to check
            
        Returns:
            True if credentials are valid, False otherwise
        """
        return username == self.username and password == self.password
    
    def is_authenticated(self) -> bool:
        """
        Check if the current session is authenticated.
        
        Returns:
            True if authenticated, False otherwise
        """
        return st.session_state.get("authenticated", False)
    
    def login(self, username: str, password: str) -> bool:
        """
        Attempt to log in with provided credentials.
        
        Args:
            username: Username to authenticate
            password: Password to authenticate
            
        Returns:
            True if login successful, False otherwise
        """
        if self.check_credentials(username, password):
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            return True
        return False
    
    def logout(self):
        """Log out the current user."""
        st.session_state["authenticated"] = False
        if "username" in st.session_state:
            del st.session_state["username"]
    
    def get_current_user(self) -> str:
        """
        Get the current authenticated username.
        
        Returns:
            Username if authenticated, empty string otherwise
        """
        return st.session_state.get("username", "")


def show_login_page():
    """Display the login page."""
    st.title("🔐 Authentication Required")
    st.markdown("Please log in to access the Follow-up Questions Manager.")
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.subheader("Login")
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            login_button = st.form_submit_button("🔑 Login", type="primary", use_container_width=True)
            
            if login_button:
                if username and password:
                    auth_manager = AuthManager()
                    if auth_manager.login(username, password):
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password.")
                else:
                    st.error("❌ Please enter both username and password.")
    
    # Add some styling and information
    st.markdown("---")
    st.info("💡 **For administrators:** Set AUTH_USERNAME and AUTH_PASSWORD in your .env file.")
    
    # Add some space and footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "<small>Follow-up Questions Manager - Secure Access</small>"
        "</div>", 
        unsafe_allow_html=True
    )


def require_authentication():
    """
    Decorator-like function to require authentication.
    Call this at the beginning of your main app function.
    
    Returns:
        AuthManager instance if authenticated, None if not authenticated
    """
    auth_manager = AuthManager()
    
    if not auth_manager.is_authenticated():
        show_login_page()
        return None
    
    return auth_manager


def show_logout_button():
    """Show logout button in sidebar."""
    auth_manager = AuthManager()
    current_user = auth_manager.get_current_user()
    
    if current_user:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"👤 **Logged in as:** {current_user}")
        
        if st.sidebar.button("🚪 Logout", type="secondary", use_container_width=True):
            auth_manager.logout()
            st.rerun()
