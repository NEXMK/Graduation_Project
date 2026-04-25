import sys
import os

# Diagnostic: Print folder contents to logs to see what's happening on the server
print(f"--- DIAGNOSTICS ---")
print(f"Current Working Directory: {os.getcwd()}")
print(f"Files in root: {os.listdir('.')}")
if os.path.exists('streamlit_thesys'):
    print(f"Contents of streamlit_thesys: {os.listdir('streamlit_thesys')}")
else:
    print("WARNING: streamlit_thesys folder NOT FOUND in root!")

# Force current directory into path
sys.path.insert(0, os.getcwd())

import streamlit as st
from streamlit_thesys import visualize, render_response
from streamlit_thesys.demo_data import DEFAULT_USER_MESSAGE, DEMO_DATA_OPTIONS
from openai import OpenAI
from typing import Any
import os
import json
import pandas as pd

# Must be the first Streamlit command
st.set_page_config(page_title="ChatCSV - Talk to your data", layout="wide")

# Inject Custom CSS for the Landing Page and Dark Mode
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@400;500;700&display=swap');

/* CSS variables and global settings */
.stApp {
    background-color: #07070f;
    background-image:
        radial-gradient(ellipse 80% 60% at 70% -10%, rgba(79,70,229,0.22) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at -10% 80%, rgba(168,85,247,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 90% 90%, rgba(56,189,248,0.12) 0%, transparent 60%);
    color: #f8fafc;
    font-family: 'Inter', sans-serif;
    min-height: 100vh;
}

/* Subtle dot-grid overlay for texture */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background-image: radial-gradient(circle, rgba(255,255,255,0.04) 1px, transparent 1px);
    background-size: 32px 32px;
}

/* Ensure app content sits above the pseudo overlay */
.stApp > * { position: relative; z-index: 1; }

/* Animated floating orbs keyframes */
@keyframes orb-float-1 {
    0%,100% { transform: translate(0,0) scale(1); }
    33%      { transform: translate(30px,-40px) scale(1.08); }
    66%      { transform: translate(-20px, 20px) scale(0.95); }
}
@keyframes orb-float-2 {
    0%,100% { transform: translate(0,0) scale(1); }
    40%     { transform: translate(-35px, 25px) scale(1.1); }
    70%     { transform: translate(20px,-15px) scale(0.9); }
}
@keyframes orb-float-3 {
    0%,100% { transform: translate(0,0) scale(1); }
    50%     { transform: translate(25px, 35px) scale(1.05); }
}

/* Background Effects (landing page animated orbs) */
.background-effects {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: -1;
    overflow: hidden;
    pointer-events: none;
}
.glow-orb { position: absolute; border-radius: 50%; filter: blur(90px); opacity: 0.35; }
.orb-1 {
    top: -10%; right: 10%; width: 520px; height: 520px;
    background: radial-gradient(circle, #4f46e5 0%, transparent 70%);
    animation: orb-float-1 14s ease-in-out infinite;
}
.orb-2 {
    bottom: 15%; left: 2%; width: 380px; height: 380px;
    background: radial-gradient(circle, #a855f7 0%, transparent 70%);
    animation: orb-float-2 18s ease-in-out infinite;
}
.orb-3 {
    top: 40%; right: 28%; width: 300px; height: 300px;
    background: radial-gradient(circle, #38bdf8 0%, transparent 70%);
    animation: orb-float-3 12s ease-in-out infinite;
}

/* Navbar styling */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 2rem;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
}
.nav-brand {
    font-size: 5rem; /* Doubled font size */
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: 1px;
}
.nav-actions {
    display: flex;
    gap: 1rem;
}
.nav-btn {
    background: transparent;
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 0.5rem 1.5rem;
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
}
.nav-btn:hover {
    background: rgba(255, 255, 255, 0.1);
}
.nav-btn.primary {
    background: #4f46e5;
    border: none;
}
.nav-btn.primary:hover {
    background: #6366f1;
}

/* Typography and Layout */
.hero-section { text-align: center; padding: 6rem 1rem 2rem; margin-top: 1rem; }
.badge { display: inline-block; padding: 0.4rem 1rem; background: rgba(56, 189, 248, 0.1); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 20px; font-size: 0.875rem; font-weight: 500; margin-bottom: 2rem; }
.hero-title { font-size:  clamp(6rem, 10vw, 9rem); font-family: 'Outfit', sans-serif; font-weight: 800; line-height: 1.2; margin-bottom: 2rem; color: #fff; } /* Doubled hero-title size */
.gradient-text { background: linear-gradient(135deg, #38bdf8, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero-subtitle { font-size: 2rem; color: #94a3b8; max-width: 900px; margin: 0 auto 3rem; text-align: center; line-height: 1.6; }

/* Features Cards */
.features-grid { display: flex; gap: 2rem; justify-content: center; flex-wrap: wrap; margin-top: 4rem; padding-bottom: 2rem; }
.feature-card { background: rgba(20, 20, 24, 0.7); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 2rem; width: 300px; text-align: left; }
.feature-icon { font-size: 2.5rem; margin-bottom: 1rem; }
.feature-card h3 { margin-bottom: 0.5rem; font-family: 'Outfit', sans-serif; font-size: 1.25rem; color: #fff; }
.feature-card p { color: #94a3b8; font-size: 0.95rem; line-height: 1.5; }

/* How It Works Steps */
.how-it-works { margin: 3rem auto 6rem; max-width: 800px; text-align: left; }
.how-it-works-title { text-align: center; font-family: 'Outfit', sans-serif; font-size: 2rem; margin-bottom: 3rem; color: #fff; }
.step-container { display: flex; flex-direction: column; gap: 1.5rem; }
.step { display: flex; align-items: center; gap: 1.5rem; background: rgba(20, 20, 24, 0.7); backdrop-filter: blur(16px); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); }
.step-number { background: #4f46e5; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-family: 'Outfit', sans-serif; font-size: 1.2rem; flex-shrink: 0;}
.step-text { color: #f8fafc; font-size: 1.1rem; }

/* Override main Streamlit Start Button */
.stButton > button.st-emotion-cache-1s326q0,
.stButton > button {
    border-radius: 8px !important;
    font-weight: 900 !important;
    font-size: 1.2rem !important;
    transition: transform 0.3s ease !important;
    
}
.stButton > button[data-baseweb="button"] { border: 1px solid rgba(255, 255, 255, 0.2) !important; padding: 1rem 2rem !important; }
.stButton > button[data-baseweb="button"]:hover { transform: translateY(-2px); border-color: #fff !important; }
.stButton > button[kind="primary"] { background: #4f46e5 !important; border: none !important; }
.stButton > button[kind="primary"]:hover { background: #6366f1 !important; transform: translateY(-2px); border: none !important; }

/* === MODERN TAB STYLES === */
/* Tab bar background */
[data-testid="stTabs"] [role="tablist"] {
    background: rgba(20, 20, 28, 0.8) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    gap: 4px !important;
    backdrop-filter: blur(12px) !important;
}
/* Individual tab buttons */
[data-testid="stTabs"] [role="tab"] {
    background: transparent !important;
    color: #94a3b8 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    padding: 0.45rem 1.4rem !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.01em !important;
}
/* Hover state */
[data-testid="stTabs"] [role="tab"]:hover {
    color: #ffffff !important;
    background: rgba(255,255,255,0.06) !important;
}
/* Active / selected tab */
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #4f46e5, #6366f1) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 12px rgba(79,70,229,0.45) !important;
}
/* Remove default Streamlit tab underline indicator */
[data-testid="stTabs"] [role="tab"][aria-selected="true"]::after,
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    display: none !important;
    background: transparent !important;
}
/* Tab content area */
[data-testid="stTabs"] [data-baseweb="tab-panel"] {
    border-top: 1px solid rgba(255,255,255,0.07) !important;
    padding-top: 1.5rem !important;
}

/* Hide top header by default to make it look like a real page */
header {visibility: hidden;}

/* === WHITE LABELS === */
/* Make specific widget labels white */
[data-testid="stFileUploader"] label,
[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] p,
.stFileUploader label p,
div[data-testid="stWidgetLabel"] > div > p,
div[data-testid="stWidgetLabel"] p {
    color: #ffffff !important;
}

/* === BROWSE FILES BUTTON STYLE === */
/* Target Streamlit's file uploader 'Browse files' button */
[data-testid="stFileUploaderDropzoneInstructions"] + div button,
[data-testid="stFileUploader"] button,
button[data-testid="baseButton-secondary"][kind="secondary"] {
    background: #4f46e5 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.2rem !important;
    transition: background 0.2s ease !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] + div button:hover,
/* === MODAL & THEME TOGGLE STYLES === */
/* Theme Override for Streamlit App */
[data-theme="light"] .stApp {
    background-color: #f0f4ff !important;
    background-image: none !important;
    color: #0f172a !important;
}
[data-theme="light"] .hero-title, [data-theme="light"] .how-it-works-title, [data-theme="light"] .feature-card h3 {
    color: #0f172a !important;
}
[data-theme="light"] .hero-subtitle, [data-theme="light"] .step-text, [data-theme="light"] .feature-card p {
    color: #475569 !important;
}
[data-theme="light"] .feature-card, [data-theme="light"] .step {
    background: rgba(255, 255, 255, 0.8) !important;
    border-color: rgba(0, 0, 0, 0.1) !important;
}
[data-theme="light"] .nav-brand { color: #0f172a !important; }
[data-theme="light"] .nav-btn { color: #0f172a !important; border-color: rgba(0,0,0,0.2) !important; }
[data-theme="light"] .nav-btn:hover { background: rgba(0,0,0,0.05) !important; }

/* Theme Toggle Button */
.theme-toggle {
    display: flex; align-items: center; justify-content: center;
    width: 40px; height: 40px; border-radius: 50%;
    border: 1px solid rgba(255, 255, 255, 0.2);
    background: transparent;
    cursor: pointer; font-size: 1.15rem;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    color: white; margin-left: 0.5rem;
}
.theme-toggle:hover { border-color: #4f46e5; transform: rotate(20deg) scale(1.1); }
.icon-sun  { display: inline; line-height: 1; }
.icon-moon { display: none;   line-height: 1; }
[data-theme="light"] .theme-toggle { color: #0f172a; border-color: rgba(0,0,0,0.2); }
[data-theme="light"] .icon-sun  { display: none; }
[data-theme="light"] .icon-moon { display: inline; }

/* Modal CSS */
.modal-backdrop {
    display: none; position: fixed; inset: 0; z-index: 999999;
    background: rgba(0,0,0,0.65); backdrop-filter: blur(6px);
    align-items: center; justify-content: center; padding: 1rem;
}
.modal-backdrop.open { display: flex; }
.modal-card {
    width: 100%; max-width: 440px; background: rgba(20, 20, 24, 0.95);
    backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    overflow: hidden; animation: cardSlideIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    font-family: 'Inter', sans-serif;
}
[data-theme="light"] .modal-card { background: rgba(255, 255, 255, 0.95); border-color: rgba(0,0,0,0.1); }
@keyframes cardSlideIn { from { opacity: 0; transform: translateY(30px) scale(0.95); } to { opacity: 1; transform: translateY(0) scale(1); } }
.modal-tabs { display: flex; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding: 0 1.5rem; gap: 0.25rem; }
[data-theme="light"] .modal-tabs { border-color: rgba(0,0,0,0.1); }
.modal-tab {
    background: none; border: none; color: #94a3b8; font-family: 'Inter', sans-serif;
    font-size: 1rem; font-weight: 600; padding: 1.1rem 1rem; cursor: pointer;
    border-bottom: 2px solid transparent; margin-bottom: -1px; transition: color 0.2s;
}
.modal-tab:hover { color: #f8fafc; }
[data-theme="light"] .modal-tab:hover { color: #0f172a; }
.modal-tab.active { color: #4f46e5; border-bottom-color: #4f46e5; }
.modal-close { margin-left: auto; background: none; border: none; color: #94a3b8; font-size: 1.1rem; cursor: pointer; padding: 0.4rem; border-radius: 6px; }
.modal-close:hover { color: #f8fafc; background: rgba(255,255,255,0.08); }
[data-theme="light"] .modal-close:hover { color: #0f172a; background: rgba(0,0,0,0.06); }
.modal-panel { display: none; padding: 1.75rem 2rem 2rem; }
.modal-panel.active { display: block; }
.modal-subtitle { font-size: 0.95rem; color: #94a3b8; margin-bottom: 1.5rem; margin-top: 0; }
.auth-form { display: flex; flex-direction: column; gap: 1.1rem; }
.field-group { display: flex; flex-direction: column; gap: 0.4rem; text-align: left; }
.field-group > label { font-size: 0.85rem; font-weight: 600; color: #f8fafc; }
[data-theme="light"] .field-group > label { color: #0f172a; }
.input-wrapper {
    display: flex; align-items: center; background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden;
}
[data-theme="light"] .input-wrapper { background: rgba(0,0,0,0.03); border-color: rgba(0,0,0,0.1); }
.input-wrapper:focus-within { border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79,70,229,0.18); }
.input-icon { padding: 0 0.75rem; font-size: 0.95rem; }
.input-wrapper input {
    flex: 1; background: none; border: none; outline: none; padding: 0.7rem 0.5rem 0.7rem 0;
    font-family: 'Inter', sans-serif; font-size: 0.95rem; color: #f8fafc; min-width: 0;
}
[data-theme="light"] .input-wrapper input { color: #0f172a; }
.input-wrapper input::placeholder { color: #94a3b8; }
.toggle-pw { background: none; border: none; cursor: pointer; padding: 0 0.75rem; color: #94a3b8; }
.form-row { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; }
.checkbox-label { display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; color: #94a3b8; cursor: pointer; }
.forgot-link { font-size: 0.85rem; color: #4f46e5; text-decoration: none; }
.btn-full { background: #4f46e5; color: white; border: none; padding: 0.8rem; border-radius: 8px; font-weight: 600; cursor: pointer; width: 100%; font-size: 1rem; margin-top: 0.25rem; }
.btn-full:hover { background: #6366f1; }
.switch-text { text-align: center; font-size: 0.875rem; color: #94a3b8; margin-top: 0.5rem; }
.link-btn { background: none; border: none; color: #4f46e5; font-weight: 600; cursor: pointer; font-size: inherit; }
.link-btn:hover { text-decoration: underline; }
.input-wrapper.error { border-color: #ef4444; box-shadow: 0 0 0 3px rgba(239,68,68,0.18); }
.field-error { font-size: 0.78rem; color: #ef4444; margin-top: -0.2rem; margin-bottom: 0; }
</style>
""", unsafe_allow_html=True)

# Application State
if 'app_started' not in st.session_state:
    st.session_state.app_started = False

if not st.session_state.app_started:
    # --- LANDING PAGE VIEW ---
    st.markdown("""
    <div class="background-effects">
        <div class="glow-orb orb-1"></div>
        <div class="glow-orb orb-2"></div>
        <div class="glow-orb orb-3"></div>
    </div>
    
    <div class="navbar">
        <div class="nav-brand">DataChat</div>
        <div class="nav-actions">
            <button class="nav-btn" id="navBtnSignIn">Sign In</button>
            <button class="nav-btn primary" id="navBtnSignUp">Sign Up</button>
            <button class="theme-toggle" id="themeToggleBtn" aria-label="Toggle light/dark mode">
                <span class="icon-sun">☀️</span>
                <span class="icon-moon">🌙</span>
            </button>
        </div>
    </div>
    
    <div class="hero-section">
        <div class="badge">✨ AI-Powered Data Analysis</div>
        <h1 class="hero-title">
            Talk to Your <span class="gradient-text">CSV Data</span> <br> Like a Colleague
        </h1>
        <p class="hero-subtitle" style="text-align: center; margin-left: auto; margin-right: auto;">
            Upload your dataset and start discovering insights immediately. Our intelligent platform automatically analyzes your files and lets you ask questions in plain English to generate reports in seconds.
        </p>
    </div>

    <!-- Auth Modal Injected Here -->
    <div class="modal-backdrop" id="authBackdrop">
        <div class="modal-card">
            <div class="modal-tabs">
                <button class="modal-tab active" id="tabSignIn">Sign In</button>
                <button class="modal-tab" id="tabSignUp">Sign Up</button>
                <button class="modal-close" id="modalClose">✕</button>
            </div>
            <!-- Sign In -->
            <div class="modal-panel active" id="panelSignIn">
                <p class="modal-subtitle">Welcome back 👋</p>
                <form class="auth-form" id="formSignIn">
                    <div class="field-group">
                        <label>Email</label>
                        <div class="input-wrapper"><span class="input-icon">✉️</span><input type="email" placeholder="you@example.com" required></div>
                    </div>
                    <div class="field-group">
                        <label>Password</label>
                        <div class="input-wrapper"><span class="input-icon">🔒</span><input type="password" placeholder="••••••••" required></div>
                    </div>
                    <div class="form-row">
                        <label class="checkbox-label"><input type="checkbox"> Remember me</label>
                        <a href="#" class="forgot-link">Forgot?</a>
                    </div>
                    <button type="submit" class="btn-full">Sign In</button>
                    <p class="switch-text">Don't have an account? <button type="button" class="link-btn" id="linkToSignUp">Sign Up</button></p>
                </form>
            </div>
            <!-- Sign Up -->
            <div class="modal-panel" id="panelSignUp">
                <p class="modal-subtitle">Create your account 🚀</p>
                <form class="auth-form" id="formSignUp">
                    <div class="field-group">
                        <label>Username</label>
                        <div class="input-wrapper"><span class="input-icon">👤</span><input type="text" placeholder="coolname123" required></div>
                    </div>
                    <div class="field-group">
                        <label>Email</label>
                        <div class="input-wrapper"><span class="input-icon">✉️</span><input type="email" placeholder="you@example.com" required></div>
                    </div>
                    <div class="field-group">
                        <label>Password</label>
                        <div class="input-wrapper"><span class="input-icon">🔒</span><input type="password" placeholder="Min. 8 characters" required></div>
                    </div>
                    <div class="field-group">
                        <label class="checkbox-label"><input type="checkbox" required> I agree to the <a href="#" class="forgot-link">Terms</a></label>
                    </div>
                    <button type="submit" class="btn-full">Create Account</button>
                    <p class="switch-text">Already have an account? <button type="button" class="link-btn" id="linkToSignIn">Sign In</button></p>
                </form>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # JS Injection for Landing Page interactions via components.html
    st.components.v1.html("""
    <script>
    const mainWin = window.parent;
    const mainDoc = mainWin.document;
    
    // Auth Tabs Logic
    const switchTab = function(tab) {
        mainDoc.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
        mainDoc.querySelectorAll('.modal-panel').forEach(p => p.classList.remove('active'));
        const activeTab = mainDoc.getElementById('tab' + tab);
        const activePanel = mainDoc.getElementById('panel' + tab);
        if (activeTab) activeTab.classList.add('active');
        if (activePanel) activePanel.classList.add('active');
    };

    // Attach functionality exactly when DOM elements exist
    const attachLogic = setInterval(() => {
        const btnSignIn = mainDoc.getElementById('navBtnSignIn');
        if (btnSignIn && !btnSignIn.dataset.listenerAttached) {
            btnSignIn.dataset.listenerAttached = 'true';
            
            // Open Modal logic
            btnSignIn.addEventListener('click', () => {
                mainDoc.getElementById('authBackdrop').classList.add('open');
                switchTab('SignIn');
            });
            mainDoc.getElementById('navBtnSignUp').addEventListener('click', () => {
                mainDoc.getElementById('authBackdrop').classList.add('open');
                switchTab('SignUp');
            });

            // Close Modal logic
            mainDoc.getElementById('modalClose').addEventListener('click', () => {
                mainDoc.getElementById('authBackdrop').classList.remove('open');
            });
            mainDoc.getElementById('authBackdrop').addEventListener('click', (e) => {
                if (e.target.id === 'authBackdrop') {
                    mainDoc.getElementById('authBackdrop').classList.remove('open');
                }
            });

            // Tab Switch logic inside Modal
            mainDoc.getElementById('tabSignIn').addEventListener('click', () => switchTab('SignIn'));
            mainDoc.getElementById('tabSignUp').addEventListener('click', () => switchTab('SignUp'));
            mainDoc.getElementById('linkToSignUp').addEventListener('click', () => switchTab('SignUp'));
            mainDoc.getElementById('linkToSignIn').addEventListener('click', () => switchTab('SignIn'));

            // Form Submit Logic
            mainDoc.getElementById('formSignIn').addEventListener('submit', (e) => {
                e.preventDefault();
                mainWin.alert('Signed in! Replace with your backend call.');
                mainDoc.getElementById('authBackdrop').classList.remove('open');
            });
            mainDoc.getElementById('formSignUp').addEventListener('submit', (e) => {
                e.preventDefault();
                mainWin.alert('Account created! Replace with backend call.');
                mainDoc.getElementById('authBackdrop').classList.remove('open');
            });

            // Theme Toggle Logic
            mainDoc.getElementById('themeToggleBtn').addEventListener('click', () => {
                const current = mainDoc.body.getAttribute('data-theme') || 'dark';
                const next = current === 'dark' ? 'light' : 'dark';
                mainDoc.body.setAttribute('data-theme', next);
                mainWin.localStorage.setItem('landing-theme', next);
            });
            
            clearInterval(attachLogic);
        }
    }, 100);

    // Apply saved theme immediately on load
    const saved = mainWin.localStorage.getItem('landing-theme');
    if (saved) {
        mainDoc.body.setAttribute('data-theme', saved);
    }
    </script>
    """, height=0)

    
    # Render Streamlit Button centered
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Start Chatting Now", type="primary", use_container_width=True):
            st.session_state.app_started = True
            st.rerun()
            
    st.markdown("""
    <div class="features-grid">
        <div class="feature-card glass-card">
            <div class="feature-icon">⚡</div>
            <h3>Instant Insights</h3>
            <p>No need to write complex SQL or Python scripts. Just ask questions in plain English and get immediate answers.</p>
        </div>
        <div class="feature-card glass-card">
            <div class="feature-icon">🔒</div>
            <h3>Secure & Private</h3>
            <p>Your data is processed securely and is never used to train global models. We respect your privacy.</p>
        </div>
        <div class="feature-card glass-card">
            <div class="feature-icon">📈</div>
            <h3>Smart Visualization</h3>
            <p>Ask for charts or trends, and our AI will automatically suggest the best way to visualize your metrics.</p>
        </div>
    </div>

    <div class="how-it-works">
        <h2 class="how-it-works-title">How It Works</h2>
        <div class="step-container">
            <div class="step">
                <div class="step-number">1</div>
                <div class="step-text">Upload your data file</div>
            </div>
            <div class="step">
                <div class="step-number">2</div>
                <div class="step-text">The system analyzes the dataset</div>
            </div>
            <div class="step">
                <div class="step-number">3</div>
                <div class="step-text">Ask our chatbot any questions about your data</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # --- MAIN STREAMLIT APP VIEW ---
    st.subheader("Chat with your Data")

    # Adding a button to go back to home page
    if st.button("← Back to Home", key="back_home_btn", type="primary"):
        st.session_state.app_started = False
        st.rerun()

    st.markdown("---")

    API_KEY = st.secrets.get("THESYS_API_KEY", os.environ.get("THESYS_API_KEY", ""))

    if not API_KEY or API_KEY == "your-api-key-here":
        st.info("Get your API key from: https://console.thesys.dev")

        # Add input field for API key in the UI
        user_api_key = st.text_input(
            "Enter your Thesys API Key:",
                
            help="Your API key will be used for this session only"
        )

        if user_api_key:
            API_KEY = user_api_key
            st.success("✅ API key provided! You can now use the component below.")
        else:
            st.info("👆 Please enter your API key above to continue")
            st.stop()

    # Initialize the OpenAI client with Thesys base URL
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://api.thesys.dev/v1/embed"
    )

    # Add tabs for different functionalities
    tab1, tab2 = st.tabs(["Visualize Data", "Chat"])

    with tab1:
        col_header1, col_header2 = st.columns([8, 2])
        with col_header1:
            st.subheader("Visualize Data")
            st.write("Upload your own data file to create visualizations with Thesys.")
        with col_header2:
            if st.button("📄 Export PDF", key="export_pdf_btn", type="primary", use_container_width=True):
                st.components.v1.html(
                    """<script>window.parent.print();</script>""",
                    height=0
                )

        data_input: Any = None  # Initialize with None to allow proper type inference
        data_source = ""

        # Primary file upload section
        uploaded_file = st.file_uploader(
            "Choose a data file",
            type=['csv', 'xlsx', 'xls', 'json'],
            help="Upload CSV, Excel, or JSON files for visualization"
        )

        if uploaded_file is not None:
            try:
                # Process different file types with proper encoding handling
                if uploaded_file.name.endswith('.csv'):
                    # Try multiple encodings for CSV files
                    encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
                    data_input = None

                    for encoding in encodings_to_try:
                        try:
                            # Reset file pointer
                            uploaded_file.seek(0)
                            data_input = pd.read_csv(uploaded_file, encoding=encoding)
                            break
                        except (UnicodeDecodeError, UnicodeError):
                            continue

                    if data_input is None:
                        raise ValueError("Could not decode the CSV file with any supported encoding")

                    data_source = f"Uploaded CSV file: {uploaded_file.name}"
                    st.success(f"✅ Successfully loaded {uploaded_file.name}")
                    st.dataframe(data_input.head())

                elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                    # Excel files typically handle encoding better
                    uploaded_file.seek(0)
                    data_input = pd.read_excel(uploaded_file)
                    data_source = f"Uploaded Excel file: {uploaded_file.name}"
                    st.success(f"✅ Successfully loaded {uploaded_file.name}")
                    st.dataframe(data_input.head())

                elif uploaded_file.name.endswith('.json'):
                    # Handle JSON with proper encoding
                    uploaded_file.seek(0)
                    try:
                        # Try UTF-8 first (most common for JSON)
                        json_content = uploaded_file.read().decode('utf-8')
                        json_data = json.loads(json_content)
                    except UnicodeDecodeError:
                        # Fallback to other encodings
                        uploaded_file.seek(0)
                        json_content = uploaded_file.read().decode('utf-8-sig')
                        json_data = json.loads(json_content)

                    data_input = json_data
                    data_source = f"Uploaded JSON file: {uploaded_file.name}"
                    st.success(f"✅ Successfully loaded {uploaded_file.name}")
                    st.json(data_input)

            except ValueError as e:
                st.error(f"❌ Encoding error: {str(e)}")
                st.info("💡 Try saving your file with UTF-8 encoding, or use Excel format (.xlsx) instead.")
                data_input = None
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
                st.info("Please check your file format and try again.")
                data_input = None

        # Demo data option (only show if no file uploaded)
        if uploaded_file is None:
            demo_option = st.selectbox(
                "Or choose a demo dataset:",
                list(DEMO_DATA_OPTIONS.keys()),
                help="Select from various demo datasets to test visualization"
            )

            if st.button("Load Demo Data", key="load_demo", type="primary"):
                # Store demo data in session state
                st.session_state.demo_data = DEMO_DATA_OPTIONS[demo_option]()
                st.session_state.demo_data_source = f"Demo dataset: {demo_option}"
                st.session_state.demo_data_name = demo_option

        # Check if demo data is loaded in session state
        if uploaded_file is None and hasattr(st.session_state, 'demo_data'):
            data_input = st.session_state.demo_data
            data_source = st.session_state.demo_data_source
            st.success(f"Loaded demo dataset: {st.session_state.demo_data_name}")
            st.dataframe(data_input.head())

            # Add button to clear demo data
            if st.button("Clear Demo Data", key="clear_demo"):
                del st.session_state.demo_data
                del st.session_state.demo_data_source
                del st.session_state.demo_data_name
                st.rerun()

        # Instructions and generate button
        if data_input is not None:
            st.markdown("---")
            st.markdown("### Visualization Instructions")
            instructions = st.text_area(
                "Instructions (optional):",
                value="",
                help="Provide specific instructions for how you want the data visualized. Leave empty for automatic visualization.",
                placeholder="e.g., 'Create a bar chart showing sales by month' or 'Generate a line graph with trend analysis'"
            )

            # Generate visualization button
            if st.button("Generate Visualization", type="primary", key="visualize_btn"):
                with st.spinner(f"Calling Thesys Visualize API with {data_source.lower()}..."):
                    # Call the thesys_visualize function with instructions
                    visualize(instructions=instructions, data=data_input, api_key=API_KEY)
        else:
            st.info("📤 Upload a file above or load demo data to get started.")


    with tab2:
        # User input for custom messages
        user_message = st.text_input("Enter your message:",
                                     value=DEFAULT_USER_MESSAGE,
                                     help="Type a message to send to LLM")

        if st.button("Send Message", type="primary"):
            with st.spinner("Calling Thesys C1 API..."):
                try:
                    # Send the user message to the Thesys C1 API
                    response = client.chat.completions.create(
                        model="c1/anthropic/claude-sonnet-4/v-20250815",
                        messages=[
                            {"role": "user", "content": user_message}
                        ],
                    )

                    # Extract the response content
                    c1_response = response.choices[0].message.content

                    st.success("✅ Successfully received response from Thesys C1 API")

                    # Store the response in session state for persistence
                    st.session_state.c1_response = c1_response

                except Exception as e:
                    st.error(f"❌ Error calling Thesys API: {str(e)}")
                    st.info("Make sure you have a valid API key and internet connection")
                    # Fallback to a demo response
                    st.session_state.c1_response = f"Demo response for: '{user_message}' - This is a fallback since the API call failed."

        # Render the response using the Thesys component
        if hasattr(st.session_state, 'c1_response'):
            st.subheader("C1 Component Response:")
            action = render_response(st.session_state.c1_response)
            if action:
                st.write("User indicated the next turn . Next action:")
                st.write(action)
        else:
            st.info("👆 Click 'Send Message' to see the Thesys C1 component in action!")
