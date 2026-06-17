import streamlit as st
import pdfplumber
import os
import textwrap
import re
import time
import json
from pathlib import Path

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="LegalAstra | AI Contract Analysis",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. MODERN CUSTOM CSS (HIGH-CONTRAST BLACK & WHITE THEME) ---
st.markdown("""
    <style>
    /* Overall Background and Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Apply Inter font gracefully without breaking Streamlit's Material Icons */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Protect the Streamlit icons from being overwritten by text fonts */
    .material-symbols-rounded, .material-icons {
        font-family: 'Material Symbols Rounded' !important;
    }
    
    .stApp {
        background: #f8f9fa;
        color: #111111;
    }
    
    /* Professional Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
        color: #000000 !important;
    }
    
    /* Hide the default Streamlit App Menu but keep the Sidebar Toggle */
    #MainMenu {visibility: hidden;}
    [data-testid="stHeaderActionElements"] {display: none;}
    header {background: transparent !important;}
    
    /* Sidebar Deep Dark Mode (The Black & White Mix) */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a !important;
        border-right: 1px solid #222222;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: #333333 !important;
    }
    
    /* Top Navbar Styling */
    .navbar-container {
        padding: 10px 0px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Modern Cards (High Contrast White) */
    .modern-card {
        background: #ffffff;
        border: 1px solid #e5e5e5;
        border-top: 6px solid #000000;
        border-radius: 8px;
        padding: 30px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .modern-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 35px -10px rgba(0, 0, 0, 0.15);
    }
    
    /* Hero Section (Deep Black for Balance) */
    .hero-container {
        text-align: center;
        padding: 80px 40px;
        background: #0a0a0a;
        border-radius: 12px;
        border: 1px solid #222222;
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        margin: 20px 0 40px 0;
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        color: #ffffff !important;
        margin-bottom: 10px;
        letter-spacing: -1.5px;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: #cccccc !important;
        margin-bottom: 30px;
        font-weight: 400;
    }
    
    /* Call to Action Black Banner */
    .cta-banner {
        text-align: center;
        margin: 40px 0;
        background: #0a0a0a;
        padding: 50px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    
    /* FORCE header inside cta-banner to be white */
    .cta-banner h3 {
        color: #ffffff !important;
    }
    .cta-banner p {
        color: #cccccc !important;
    }
    
    /* Summary & Risk Boxes */
    .summary-box {
        background: #ffffff;
        border-left: 5px solid #000000;
        padding: 25px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border-top: 1px solid #f0f0f0;
        border-right: 1px solid #f0f0f0;
        border-bottom: 1px solid #f0f0f0;
        color: #212529;
        line-height: 1.8;
    }
    
    .client-box {
        background: #ffffff;
        border-left: 5px solid #6c757d;
        padding: 25px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border-top: 1px solid #f0f0f0;
        border-right: 1px solid #f0f0f0;
        border-bottom: 1px solid #f0f0f0;
        color: #212529;
        line-height: 1.8;
    }
    
    .risk-high {
        background: #fffafa;
        border-left: 5px solid #dc3545;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        border-top: 1px solid #ffeaea;
        border-right: 1px solid #ffeaea;
        border-bottom: 1px solid #ffeaea;
        color: #b02a37;
    }
    
    .risk-medium {
        background: #fffdf5;
        border-left: 5px solid #ffc107;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        border-top: 1px solid #fff8e1;
        border-right: 1px solid #fff8e1;
        border-bottom: 1px solid #fff8e1;
        color: #997404;
    }
    
    /* Stats Cards (Inverted to Black) */
    .stat-card {
        background: #0a0a0a;
        border: 1px solid #222222;
        border-radius: 10px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .stat-number {
        font-size: 3rem;
        font-weight: 800;
        color: #ffffff !important;
    }
    
    .stat-label {
        color: #aaaaaa !important;
        font-size: 1rem;
        margin-top: 8px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #6c757d;
        font-size: 0.85rem;
        margin-top: 80px;
        padding: 30px;
        border-top: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 1px solid #000000 !important;
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    .stButton > button:hover {
        background-color: #f0f0f0 !important;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: none !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #333333 !important;
        color: #ffffff !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        border-bottom: 2px solid #e5e5e5;
    }
    .stTabs [data-baseweb="tab"] {
        color: #6c757d;
        border-radius: 6px 6px 0 0;
    }
    .stTabs [aria-selected="true"] {
        color: #000000 !important;
        border-bottom: 3px solid #000000 !important;
        font-weight: 600;
    }
    
    /* Custom Sidebar Navigation Buttons */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 8px !important;
        padding: 12px 15px !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        margin-bottom: 5px !important;
        display: flex !important;
        justify-content: flex-start !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-color: #ffffff !important;
        transform: translateX(4px);
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. PERSISTENCE FUNCTIONS ---
USERS_FILE = Path("users_data.json")

def load_users_from_file():
    """Load user data from JSON file"""
    if USERS_FILE.exists():
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users_to_file(users_dict):
    """Save user data to JSON file"""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users_dict, f, indent=2)
    except Exception as e:
        st.error(f"Error saving user data: {e}")

# --- 4. SESSION STATE INITIALIZATION ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = ""
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'show_welcome' not in st.session_state:
    st.session_state['show_welcome'] = False
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = "Dashboard"

# AI Outputs & Data Memory State
if 'raw_text' not in st.session_state:
    st.session_state['raw_text'] = None
if 'current_file_name' not in st.session_state:
    st.session_state['current_file_name'] = ""
if 'summary_text' not in st.session_state:
    st.session_state['summary_text'] = None
if 'risk_results' not in st.session_state:
    st.session_state['risk_results'] = None
if 'scanned_for_risks' not in st.session_state:
    st.session_state['scanned_for_risks'] = False
    
# Load users from persistent file
if 'users' not in st.session_state:
    st.session_state['users'] = load_users_from_file()

# Modal visibility states
if 'show_login_modal' not in st.session_state:
    st.session_state['show_login_modal'] = False
if 'show_signup_modal' not in st.session_state:
    st.session_state['show_signup_modal'] = False

# --- 4. AI MODEL LOADING (CACHED) ---
@st.cache_resource
def load_summarization_model():
    """Loads the AI summarizer directly to avoid pipeline KeyErrors."""
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    import torch
    sum_tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")
    sum_model = AutoModelForSeq2SeqLM.from_pretrained("sshleifer/distilbart-cnn-12-6")
    return sum_tokenizer, sum_model

@st.cache_resource
def load_risk_detection_model():
    """Loads the Zero-Shot Classification model."""
    from transformers import pipeline
    import torch
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", framework="pt")
    return classifier

# --- 5. HELPER FUNCTIONS ---
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text

def chunk_text(text, max_words=400):
    words = text.split()
    chunks = [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]
    return chunks

def clear_summary_cache():
    """Clears the summary cache when the length slider is adjusted"""
    st.session_state['summary_text'] = None

# --- 6. MODAL DIALOGS FOR AUTH ---
@st.dialog("🔐 Login to LegalAstra", width="large")
def login_modal():
    """Modal dialog for user login"""
    st.markdown("### Sign in to your account")
    st.markdown("Access your legal documents and AI analysis.")
    st.divider()
    
    with st.form("login_form"):
        login_email = st.text_input("📧 Email Address", placeholder="you@gmail.com")
        login_password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("🚀 Login", use_container_width=True, type="primary"):
                login_email_clean = login_email.lower().strip()
                if login_email_clean in st.session_state['users'] and st.session_state['users'][login_email_clean]['password'] == login_password:
                    user_data = st.session_state['users'][login_email_clean]
                    st.session_state['username'] = user_data['name']
                    st.session_state['user_role'] = user_data['role']
                    st.session_state['logged_in'] = True
                    st.session_state['show_welcome'] = True
                    st.toast(f"✨ Welcome back, {user_data['name']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password. Please try again.")
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.rerun()

@st.dialog("✍️ Create Your Account", width="large")
def signup_modal():
    """Modal dialog for user registration"""
    st.markdown("### Join LegalAstra Today")
    st.markdown("Start analyzing legal documents with AI in seconds.")
    st.divider()
    
    with st.form("signup_form"):
        reg_name = st.text_input("👤 Full Name", placeholder="John Doe")
        reg_email = st.text_input("📧 Email Address", placeholder="you@gmail.com")
        reg_password = st.text_input("🔑 Password", type="password", placeholder="Create a strong password")
        reg_role = st.selectbox("👨‍⚖️ I am a:", ["Client", "Lawyer"])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("✅ Create Account", use_container_width=True, type="primary"):
                reg_email_clean = reg_email.lower().strip()
                email_pattern = r"^[a-zA-Z0-9_.+-]+@gmail\.com$"
                
                if not reg_name.strip():
                    st.error("❌ Please enter your full name.")
                elif not re.match(email_pattern, reg_email_clean):
                    st.error("❌ Please use a valid Gmail address (@gmail.com).")
                elif reg_email_clean in st.session_state['users']:
                    st.error("❌ This email is already registered!")
                elif not reg_password.strip() or len(reg_password) < 6:
                    st.error("❌ Password must be at least 6 characters.")
                else:
                    st.session_state['users'][reg_email_clean] = {
                        "name": reg_name.strip(),
                        "password": reg_password,
                        "role": reg_role
                    }
                    # Save to file
                    save_users_to_file(st.session_state['users'])
                    st.success("🎉 Account created successfully! Please log in.")
                    time.sleep(1.5)
                    st.rerun()
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.rerun()

# --- 7. TOP NAVIGATION BAR (PERSISTENT) ---
def render_navbar():
    """Renders the professional legal tech navigation bar"""
    col_logo, col_spacer, col_auth = st.columns([3, 2.5, 2])
    
    with col_logo:
        # Changed ratio to make the logo significantly larger
        c1, c2 = st.columns([0.3, 0.7])
        with c1:
            # LOGO RENDERING
            if os.path.exists("logo.png"):
                st.image("logo.png", use_container_width=True)
            else:
                st.markdown("<h1 style='margin:0; padding-top: 0px;'>⚖️</h1>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div style='margin-top: 5px;'>
                <span style='font-size: 1.8rem; font-weight: 800; color: #000; letter-spacing: -0.5px;'>LegalAstra</span>
                <div style='font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-top: -5px;'>AI Platform</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_auth:
        if st.session_state['logged_in']:
            c_space, c_profile = st.columns([1, 1.5])
            with c_profile:
                with st.popover(f"👤 {st.session_state['username']}", use_container_width=True):
                    st.markdown("### 👤 Profile")
                    st.markdown(f"""
                    <div style='padding: 5px; color: #333;'>
                        <div style='margin-bottom: 10px;'><b style='color: #000;'>Name:</b><br><span>{st.session_state['username']}</span></div>
                        <div style='margin-bottom: 10px;'><b style='color: #000;'>Role:</b><br><span>{st.session_state['user_role']}</span></div>
                        <div><b style='color: #000;'>Status:</b><br><span style='color: #28a745; font-weight: 600;'>✅ Connected</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.divider()
                    if st.button("🚪 Logout", use_container_width=True, key="dropdown_logout"):
                        st.session_state['logged_in'] = False
                        st.session_state['user_role'] = ""
                        st.session_state['username'] = ""
                        st.session_state['current_page'] = "Dashboard"
                        st.session_state['raw_text'] = None
                        st.session_state['current_file_name'] = ""
                        st.session_state['summary_text'] = None
                        st.session_state['risk_results'] = None
                        st.session_state['scanned_for_risks'] = False
                        st.toast("👋 Logged out successfully!")
                        st.rerun()
        else:
            col_login, col_signup = st.columns(2)
            with col_login:
                if st.button("🔐 Login", use_container_width=True, key="navbar_login"):
                    login_modal()
            with col_signup:
                if st.button("✍️ Sign Up", use_container_width=True, type="primary", key="navbar_signup"):
                    signup_modal()
    
    st.divider()

# --- 6. APP ROUTING (ALWAYS VISIBLE) ---
render_navbar()

# Welcome Toast
if st.session_state.get('show_welcome'):
    role_emoji = "⚖️" if st.session_state['user_role'] == "Lawyer" else "📋"
    st.toast(f"{role_emoji} Welcome, {st.session_state['username']}! Ready to analyze contracts?")
    st.session_state['show_welcome'] = False

# --- 8. SIDEBAR NAVIGATION (ONLY WHEN LOGGED IN) ---
if st.session_state['logged_in']:
    with st.sidebar:
        # SIDEBAR HEADER
        st.markdown("""
        <div style='text-align: center; padding: 20px 0; border-bottom: 2px solid #333333;'>
            <div style='font-size: 2.5rem; margin-bottom: 8px;'>⚖️</div>
            <h2 style='margin: 0; padding: 0; color: #ffffff !important; font-size: 1.4rem; letter-spacing: -0.5px;'>LegalAstra</h2>
            <p style='margin: 5px 0 0 0; color: #888888; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;'>AI Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        
        # NAVIGATION SECTION
        st.markdown("""
        <div style='color: #ffffff; font-weight: 700; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; margin: 15px 0 10px 0; color: #cccccc;'>
            🧭 Navigation
        </div>
        """, unsafe_allow_html=True)
        
        # Redesigned Stacked Navigation Buttons
        if st.button("📊 Dashboard", use_container_width=True, key="nav_dashboard"):
            st.session_state['current_page'] = "Dashboard"
            st.rerun()
            
        if st.button("📖 Guide", use_container_width=True, key="nav_guide"):
            st.session_state['current_page'] = "Guide"
            st.rerun()
            
        if st.button("ℹ️ About", use_container_width=True, key="nav_about"):
            st.session_state['current_page'] = "About"
            st.rerun()
        
        # Highlight current page (High Visibility Box with sleek transparent design)
        st.markdown(f"""
        <div style='text-align: center; padding: 15px; background: transparent; border: 2px solid #ffffff; border-radius: 8px; color: #ffffff !important; font-size: 1rem; margin-top: 15px; font-weight: 800;'>
            📍 Active: {st.session_state['current_page']}
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # AI SETTINGS SECTION
        st.markdown("""
        <div style='color: #ffffff; font-weight: 700; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; margin: 15px 0 15px 0; color: #cccccc;'>
            ⚙️ AI Settings
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Summary Length**", help="Adjust the length of generated summaries")
        # Added on_change callback to clear old summary when length is adjusted
        summary_length = st.slider("", min_value=50, max_value=500, value=150, step=50, label_visibility="collapsed", on_change=clear_summary_cache)
        st.session_state['summary_length'] = summary_length
        
        st.markdown(f"""
        <div style='text-align: center; padding: 6px; background: #0a0a0a; border-radius: 4px; color: #888888; font-size: 0.85rem; margin-top: 5px;'>
            📝 {summary_length} words max
        </div>
        """, unsafe_allow_html=True)

# --- 9. MAIN CONTENT AREA ---

if not st.session_state['logged_in']:
    # ==========================================
    #             HERO SECTION (NOT LOGGED IN)
    # ==========================================
    
    c_hero1, c_hero2, c_hero3 = st.columns([1, 0.3, 1])
    with c_hero2:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
            
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Legal Analysis, Reimagined.</div>
        <div class="hero-subtitle">Upload, summarize, and scan legal documents for loopholes with absolute zero effort.</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="modern-card">
            <div style="font-size: 2rem; margin-bottom: 10px;">🤖</div>
            <h4>Smart AI Analysis</h4>
            <p style="color: #555555; font-size: 0.95rem;">Powered by Hugging Face Transformers for accurate contract insights.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="modern-card">
            <div style="font-size: 2rem; margin-bottom: 10px;">⚡</div>
            <h4>Lightning Fast</h4>
            <p style="color: #555555; font-size: 0.95rem;">Analyze any heavy contract in seconds, saving you hours of reading.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="modern-card">
            <div style="font-size: 2rem; margin-bottom: 10px;">🔒</div>
            <h4>Privacy First</h4>
            <p style="color: #555555; font-size: 0.95rem;">All processing happens locally. Your sensitive data stays yours.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Dark Call-to-action Banner
    st.markdown("""
    <div class="cta-banner">
        <h3 style="color: #ffffff !important; font-size: 2rem;">Get Started in 3 Steps</h3>
        <p style="color: #cccccc !important; font-size: 1.1rem; margin-bottom: 20px;">Sign up for free, upload your first contract, and let AI do the heavy lifting.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        # Pulled up slightly to overlap with the banner conceptually
        st.markdown("<div style='margin-top: -85px; text-align: center;'>", unsafe_allow_html=True)
        if st.button("✍️ Create Free Account", use_container_width=True, type="primary"):
            signup_modal()
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # ==========================================
    #          MAIN DASHBOARD (LOGGED IN)
    # ==========================================
    
    current_page = st.session_state['current_page']
    
    if current_page == "Dashboard":
        # AI MODE INDICATOR
        if st.session_state['user_role'] == "Lawyer":
            st.markdown("""
            <div class="modern-card" style="border-top: 6px solid #000; padding: 20px;">
                <b style="color:#000; font-size:1.1rem;">⚖️ Pro Lawyer Mode</b> &nbsp;|&nbsp; Displaying technical abstracts and precise AI confidence scores.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="modern-card" style="border-top: 6px solid #6c757d; padding: 20px;">
                <b style="color:#000; font-size:1.1rem;">📋 Client Mode</b> &nbsp;|&nbsp; Complex legal concepts explained in simple, plain English.
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # DOCUMENT UPLOAD SECTION
        st.markdown("### 📄 Upload Your Contract")
        
        uploaded_file = st.file_uploader("Select a PDF document", type="pdf", label_visibility="collapsed")
        
        # Process new file
        if uploaded_file is not None:
            if st.session_state['current_file_name'] != uploaded_file.name:
                with st.status("🔍 Analyzing document...", expanded=True) as status:
                    st.write("📄 Extracting text from PDF...")
                    st.session_state['raw_text'] = extract_text_from_pdf(uploaded_file)
                    st.session_state['current_file_name'] = uploaded_file.name
                    st.session_state['summary_text'] = None
                    st.session_state['risk_results'] = None
                    st.session_state['scanned_for_risks'] = False
                    status.update(label="✅ Document loaded successfully!", state="complete", expanded=False)
            
            raw_text = st.session_state['raw_text']
            
            if not raw_text.strip():
                st.error("❌ No text could be extracted. Is this a scanned image PDF?")
            else:
                text_chunks = chunk_text(raw_text)
                
                # TABS
                tab1, tab2, tab3, tab4 = st.tabs(["📝 Summary", "⚠️ Risks", "📊 Stats", "📄 Full Text"])
                
                # TAB 1: SUMMARY
                with tab1:
                    st.markdown("### 📝 Document Summary")
                    
                    summary_length = st.session_state.get('summary_length', 150)
                    
                    if st.button("✨ Generate Summary", type="primary", key="gen_summary"):
                        with st.status("Waking up the AI neural networks...", expanded=True) as status:
                            st.write("🧠 Loading DistilBART summarizer...")
                            sum_tokenizer, sum_model = load_summarization_model()
                            
                            st.write("📖 Reading legalese...")
                            summary_input = " ".join(text_chunks[:3])
                            summary_input = textwrap.shorten(summary_input, width=3000, placeholder="...")
                            
                            st.write("✍️ Generating summary...")
                            inputs = sum_tokenizer(summary_input, return_tensors="pt", max_length=1024, truncation=True)
                            
                            # Force the model to generate a longer minimum output based on the slider (70% of slider value)
                            calc_min_length = max(30, int(summary_length * 0.7))
                            
                            summary_ids = sum_model.generate(
                                inputs["input_ids"],
                                max_length=summary_length,
                                min_length=calc_min_length,
                                length_penalty=2.0, # Strongly encourage generating longer text
                                num_beams=4,
                                early_stopping=True
                            )
                            st.session_state['summary_text'] = sum_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
                            status.update(label="✅ Summary generated!", state="complete", expanded=False)
                            st.toast("✨ Summary ready!")
                    
                    if st.session_state['summary_text']:
                        if st.session_state['user_role'] == "Client":
                            st.markdown(f"""
                            <div class="client-box">
                                <h4 style="margin-top: 0;">Plain English Overview</h4>
                                <p>{st.session_state['summary_text']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="summary-box">
                                <h4 style="margin-top: 0;">Technical Abstract (DistilBART)</h4>
                                <p>{st.session_state['summary_text']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.download_button(
                            label="💾 Download Summary",
                            data=st.session_state['summary_text'],
                            file_name=f"LegalAstra_Summary_{uploaded_file.name.split('.')[0]}.txt",
                            mime="text/plain"
                        )
                    else:
                        st.info("💡 Click 'Generate Summary' to get started!")
                
                # TAB 2: RISK DETECTION
                with tab2:
                    st.markdown("### ⚠️ Risk Detection")
                    
                    risk_labels = ["Termination Clause", "Unlimited Liability", "Financial Penalty", "Confidentiality Breach", "Indemnity"]
                    
                    if st.button("🔍 Scan for Risks", type="primary", key="scan_risks"):
                        with st.status("Finding potential legal risks...", expanded=True) as status:
                            st.write("🧠 Loading BART-Large-MNLI classifier...")
                            classifier = load_risk_detection_model()
                            
                            st.write("🔎 Scanning document chunks...")
                            found_risks = []
                            
                            progress_bar = st.progress(0)
                            for idx, chunk in enumerate(text_chunks[:5]):
                                res = classifier(chunk, risk_labels, multi_label=True)
                                top_label = res['labels'][0]
                                top_score = res['scores'][0]
                                
                                if top_score > 0.60:
                                    found_risks.append({
                                        "label": top_label,
                                        "score": top_score,
                                        "chunk": chunk,
                                        "idx": idx
                                    })
                                progress_bar.progress((idx + 1) / 5)
                            
                            st.session_state['risk_results'] = found_risks
                            st.session_state['scanned_for_risks'] = True
                            status.update(label="✅ Scan complete!", state="complete", expanded=False)
                            st.toast("🔍 Risk analysis done!")
                    
                    if st.session_state['scanned_for_risks']:
                        if not st.session_state['risk_results']:
                            st.success("✅ No high-risk clauses detected in the analyzed sections!")
                        else:
                            for risk in st.session_state['risk_results']:
                                risk_class = "risk-high" if "Liability" in risk['label'] or "Penalty" in risk['label'] else "risk-medium"
                                
                                if st.session_state['user_role'] == "Client":
                                    client_translations = {
                                        "Termination Clause": "Cancellation Rules — How this contract can be ended",
                                        "Unlimited Liability": "High Financial Risk — You could be sued for unlimited amounts",
                                        "Financial Penalty": "Hidden Fines — You may have to pay extra fees",
                                        "Confidentiality Breach": "Secrecy Rules — Information you cannot share",
                                        "Indemnity": "Damage Payment Rules — Who pays if things go wrong"
                                    }
                                    friendly_label = client_translations.get(risk['label'], risk['label'])
                                    st.markdown(f"""
                                    <div class="{risk_class}">
                                        <h4 style="margin-top: 0;">⚠️ {friendly_label}</h4>
                                        <p style="margin-bottom: 10px;">The AI flagged this topic. Please read carefully.</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    with st.expander("🔍 View exact clause"):
                                        st.text(risk['chunk'][:350] + "...")
                                else:
                                    st.markdown(f"""
                                    <div class="{risk_class}">
                                        <h4 style="margin-top: 0;">{risk['label']}</h4>
                                        <p style="margin: 0;"><b>Confidence:</b> {risk['score']*100:.1f}%</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    with st.expander("🔍 View exact clause"):
                                        st.text(risk['chunk'][:400] + "...")
                    else:
                        st.info("💡 Click 'Scan for Risks' to identify potential issues!")
                
                # TAB 3: STATISTICS
                with tab3:
                    st.markdown("### 📊 Document Statistics")
                    
                    word_count = len(raw_text.split())
                    char_count = len(raw_text)
                    read_time = max(1, round(word_count / 250))
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <div class="stat-card">
                            <div class="stat-number">{word_count:,}</div>
                            <div class="stat-label">Words</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class="stat-card">
                            <div class="stat-number">{char_count:,}</div>
                            <div class="stat-label">Characters</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""
                        <div class="stat-card">
                            <div class="stat-number">{read_time}</div>
                            <div class="stat-label">Min to Read</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.info("💡 LegalAstra analyzed this entire document in seconds—saving you hours of reading time!")
                
                # TAB 4: ORIGINAL TEXT
                with tab4:
                    st.markdown("### 📄 Full Document Text")
                    st.text_area("", raw_text, height=400, disabled=True, label_visibility="collapsed")
        
        else:
            st.markdown("""
            <div class="modern-card" style="text-align: center; padding: 60px 20px;">
                <div style="font-size: 3rem; margin-bottom: 20px;">📄</div>
                <h3 style="color: #000;">Ready to analyze a contract?</h3>
                <p style="color: #555555; font-size: 1.1rem;">Upload a PDF document above to get started with AI-powered legal analysis.</p>
            </div>
            """, unsafe_allow_html=True)
    
    elif current_page == "Guide":
        st.markdown("### 📖 How to Use LegalAstra")
        st.markdown("Master the platform in just a few steps.")
        st.divider()
        
        st.markdown("""
        <div class="modern-card" style="border-top: 6px solid #000;">
            <h4>Step 1: Upload Your PDF</h4>
            <p style="color:#555;">Go to the <b>Dashboard</b> and upload any PDF contract. The AI will instantly extract the text.</p>
        </div>
        
        <div class="modern-card" style="border-top: 6px solid #000;">
            <h4>Step 2: Adjust Summary Length</h4>
            <p style="color:#555;">Use the sidebar slider to control how detailed you want the AI summary to be (50-500 words).</p>
        </div>
        
        <div class="modern-card" style="border-top: 6px solid #000;">
            <h4>Step 3: Generate Summary</h4>
            <p style="color:#555;">Click <b>Generate Summary</b> to get an AI-powered overview. For Clients, it's in plain English. For Lawyers, it's a technical abstract.</p>
        </div>
        
        <div class="modern-card" style="border-top: 6px solid #000;">
            <h4>Step 4: Scan for Risks</h4>
            <p style="color:#555;">Click <b>Scan for Risks</b> to identify critical clauses like liability limits, penalties, and confidentiality breaches.</p>
        </div>
        
        <div class="modern-card" style="border-top: 6px solid #000;">
            <h4>Step 5: Review & Download</h4>
            <p style="color:#555;">Check the full document text in the <b>Full Text</b> tab and download summaries for your records.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("💡 **Pro Tip:** Lawyer mode provides AI confidence scores. Client mode translates legal jargon into everyday language!")
    
    elif current_page == "About":
        st.markdown("### ℹ️ About LegalAstra")
        st.markdown("Transforming legal tech with intelligent AI.")
        st.divider()
        
        st.markdown("""
        <div class="modern-card" style="border-top: 6px solid #000;">
            <h4>🎯 The Mission</h4>
            <p style="color:#555;">Contracts are everywhere, but they're written in a language most people don't understand. LegalAstra uses cutting-edge AI to bridge that gap, making legal documents accessible to everyone.</p>
        </div>
        
        <div class="modern-card" style="border-top: 6px solid #000;">
            <h4>🚀 How It Works</h4>
            <ul style="color:#555;">
                <li><b style="color:#000;">Abstractive Summarization:</b> DistilBART neural network generates human-like summaries of complex documents.</li>
                <li><b style="color:#000;">Zero-Shot Risk Detection:</b> BART-Large-MNLI automatically flags critical clauses without training on specific contracts.</li>
                <li><b style="color:#000;">Role-Based Analysis:</b> Tailored insights for Lawyers (technical) and Clients (plain English).</li>
                <li><b style="color:#000;">Privacy First:</b> All processing happens locally—your documents never leave your device.</li>
            </ul>
        </div>
        
        <div class="modern-card" style="border-top: 6px solid #000;">
            <h4>🛠️ Technology Stack</h4>
            <ul style="color:#555;">
                <li><b style="color:#000;">Frontend:</b> Streamlit (Python)</li>
                <li><b style="color:#000;">AI Engine:</b> Hugging Face Transformers (PyTorch)</li>
                <li><b style="color:#000;">PDF Processing:</b> pdfplumber</li>
            </ul>
        </div>
        
        <div class="modern-card" style="border-top: 6px solid #000;">
            <h4>👥 Built By</h4>
            <p style="color:#555;">The Final Year Project Group (2026)<br>Created with 💻 & ☕ for better legal tech</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.success("🎉 Thank you for using LegalAstra! We're constantly improving. Have feedback? We'd love to hear it!")

# --- 10. FOOTER ---
st.markdown("""
<div class="footer">
    <strong>LegalAstra AI © 2026</strong> <br>
    Developed with 💻 & ☕ by the Final Year Project Group
</div>
""", unsafe_allow_html=True)