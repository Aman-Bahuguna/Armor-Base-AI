import streamlit as st
import time
from Project_core import processcommand

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ARMOR SYSTEM",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS (THE OG STYLE) ---
st.markdown("""
<style>
    /* IMPORT FUTURISTIC FONT */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Share+Tech+Mono&display=swap');

    /* BACKGROUND AND MAIN THEME */
    .stApp {
        background-color: #000000;
        background-image: radial-gradient(circle at 50% 50%, #0d1b2a 0%, #000000 100%);
        color: #00ffff;
        font-family: 'Orbitron', sans-serif;
    }

    /* GLOWING TEXT EFFECT */
    h1 {
        text-align: center;
        color: #00ffff;
        text-transform: uppercase;
        letter-spacing: 5px;
        text-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 40px #00ffff;
        font-size: 60px;
        margin-bottom: 0px;
    }

    /* PULSING CORE ANIMATION */
    .core-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;
        margin-bottom: 20px;
    }
    
    .arc-reactor {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        border: 2px solid #00ffff;
        box-shadow: 0 0 20px #00ffff, inset 0 0 20px #00ffff;
        animation: pulse 2s infinite;
        display: flex;
        justify-content: center;
        align-items: center;
        background: radial-gradient(circle, #ffffff 10%, #00ffff 60%, #000000 100%);
    }

    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 20px #00ffff; }
        50% { transform: scale(1.05); box-shadow: 0 0 40px #00ffff, 0 0 60px #00ffff; }
        100% { transform: scale(0.95); box-shadow: 0 0 20px #00ffff; }
    }

    /* CHAT HISTORY (TERMINAL STYLE) */
    .terminal-box {
        background-color: rgba(10, 15, 20, 0.9);
        border: 1px solid #00ffff;
        border-radius: 5px;
        padding: 20px;
        height: 400px;
        overflow-y: auto;
        font-family: 'Share Tech Mono', monospace;
        font-size: 16px;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.2);
    }

    .user-msg {
        color: #00ff00; /* Green for User */
        margin-bottom: 10px;
    }
    
    .armor-msg {
        color: #00ffff; /* Cyan for Armor */
        margin-bottom: 20px;
        text-shadow: 0 0 5px #00ffff;
    }

    /* INPUT FIELD STYLING */
    .stTextInput>div>div>input {
        background-color: #050505;
        color: #00ffff;
        border: 1px solid #00ffff;
        font-family: 'Share Tech Mono', monospace;
        text-align: center;
    }
    
    /* HIDE STREAMLIT ELEMENTS */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- HEADER & ANIMATION ---
st.markdown("<h1>ARMOR</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #00ffff; font-family: Share Tech Mono;'>SYSTEM ONLINE // WAITING FOR INPUT</div>", unsafe_allow_html=True)

# The Pulsing Arc Reactor Animation
st.markdown("""
<div class="core-container">
    <div class="arc-reactor"></div>
</div>
""", unsafe_allow_html=True)

# --- SESSION STATE FOR CHAT ---
if 'history' not in st.session_state:
    st.session_state['history'] = []

# --- INPUT HANDLING ---
def submit():
    user_input = st.session_state.input_field
    if user_input:
        # Add user command to history
        st.session_state['history'].append({"role": "user", "text": user_input})
        
        # Process command using Project_core logic
        response = processcommand(user_input)
        
        # Add AI response to history
        st.session_state['history'].append({"role": "armor", "text": response})
        
        # Clear input
        st.session_state.input_field = ""

# --- DISPLAY CHAT HISTORY (Terminal Style) ---
chat_html = ""
# We reverse the list to show newest messages at the top (optional, or keep standard)
for msg in reversed(st.session_state['history']):
    if msg['role'] == "user":
        chat_html += f"<div class='user-msg'>> USER: {msg['text']}</div>"
    else:
        chat_html += f"<div class='armor-msg'>> ARMOR: {msg['text']}</div>"

# Render the terminal box
st.markdown(f"<div class='terminal-box'>{chat_html}</div>", unsafe_allow_html=True)

# --- INPUT BOX ---
st.text_input("", key="input_field", on_change=submit, placeholder="ENTER COMMAND HERE...")