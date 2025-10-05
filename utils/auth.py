import streamlit as st
import json
import os
import hashlib
from datetime import datetime

USERS_FILE = "data/users.json"

def ensure_users_file():
    """Ensure users file exists"""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from JSON file"""
    ensure_users_file()
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    """Save users to JSON file"""
    ensure_users_file()
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def register_user(email, password, name):
    """Register a new user"""
    users = load_users()
    
    if email in users:
        return False, "Email already registered"
    
    users[email] = {
        'password': hash_password(password),
        'name': name,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'reported_issues': []
    }
    
    save_users(users)
    return True, "Registration successful"

def login_user(email, password):
    """Login user"""
    users = load_users()
    
    if email not in users:
        return False, "Email not found"
    
    if users[email]['password'] != hash_password(password):
        return False, "Incorrect password"
    
    return True, "Login successful"

def get_user_info(email):
    """Get user information"""
    users = load_users()
    return users.get(email)

def add_issue_to_user(email, issue_id):
    """Add issue to user's reported issues"""
    users = load_users()
    if email in users:
        if 'reported_issues' not in users[email]:
            users[email]['reported_issues'] = []
        users[email]['reported_issues'].append({
            'issue_id': issue_id,
            'reported_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        save_users(users)
        return True
    return False

def get_user_issues(email):
    """Get all issues reported by user"""
    users = load_users()
    if email in users:
        return users[email].get('reported_issues', [])
    return []

def check_authentication():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    
    return st.session_state.authenticated

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.user_name = None

def show_auth_sidebar():
    """Show authentication in sidebar"""
    if check_authentication():
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**Logged in as:** {st.session_state.user_name}")
        st.sidebar.markdown(f"📧 {st.session_state.user_email}")
        
        user_issues = get_user_issues(st.session_state.user_email)
        st.sidebar.markdown(f"**Your Issues:** {len(user_issues)}")
        
        if st.sidebar.button("Logout"):
            logout()
            st.rerun()
    else:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Not logged in**")
        st.sidebar.info("Login to track your reports")

def show_login_page():
    """Show login/register page"""
    st.header("🔐 Login / Register")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        
        with st.form("login_form"):
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if email and password:
                    success, message = login_user(email, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        user_info = get_user_info(email)
                        st.session_state.user_name = user_info['name']
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please fill in all fields")
    
    with tab2:
        st.subheader("Create New Account")
        
        with st.form("register_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Register")
            
            if submit:
                if name and email and password and confirm_password:
                    if password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        success, message = register_user(email, password, name)
                        if success:
                            st.success(message)
                            st.info("You can now login with your credentials")
                        else:
                            st.error(message)
                else:
                    st.error("Please fill in all fields")
