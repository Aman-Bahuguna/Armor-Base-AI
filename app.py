import streamlit as st
import time
import datetime
from Project_core import processcommand, listen_input, get_system_stats, get_weather

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="ARMOR AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- LOAD STATE ---
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'last_command' not in st.session_state:
    st.session_state['last_command'] = ""

# Fetch Data
cpu, ram, disk = get_system_stats()
temp, hum, wind = get_weather()
curr_time = datetime.datetime.now().strftime("%H:%M")
curr_date = datetime.datetime.now().strftime("%a, %b %d")

# --- CUSTOM CSS (Single Page, No Scroll, Clean Theme) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500&display=swap');

    /* Global Reset */
    .stApp {
        background-color: #050a14;
        font-family: 'Rajdhani', sans-serif;
        overflow: hidden; /* Prevent page scroll */
    }
    
    /* Hide Streamlit Header/Footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main Layout */
    .main-container {
        display: grid;
        grid-template-columns: 1fr 2fr 1fr;
        gap: 20px;
        height: 90vh;
        padding: 20px;
    }

    /* Cards */
    .glass-card {
        background: rgba(13, 22, 35, 0.7);
        border: 1px solid rgba(0, 224, 255, 0.2);
        box-shadow: 0 0 15px rgba(0, 224, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        color: #e0f7fa;
        backdrop-filter: blur(10px);
    }
    
    /* Reactor Animation */
    .reactor {
        width: 150px; height: 150px;
        background: radial-gradient(circle, #00e0ff 0%, #000 70%);
        border-radius: 50%;
        box-shadow: 0 0 30px #00e0ff;
        margin: 0 auto 20px auto;
        animation: pulse 3s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 20px #00e0ff; opacity: 0.8; }
        50% { box-shadow: 0 0 50px #00e0ff; opacity: 1; }
        100% { box-shadow: 0 0 20px #00e0ff; opacity: 0.8; }
    }

    /* Chat Area - Fixed Height with Scroll */
    .chat-container {
        height: 60vh;
        overflow-y: auto;
        padding-right: 10px;
        display: flex;
        flex-direction: column-reverse; /* Newest at bottom visually if we order correctly */
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #050a14; }
    ::-webkit-scrollbar-thumb { background: #00e0ff; border-radius: 3px; }

    /* Message Bubbles */
    .msg-user { text-align: right; color: #00ff99; margin: 5px 0; font-size: 1.1rem; }
    .msg-ai { text-align: left; color: #00e0ff; margin: 5px 0; border-left: 3px solid #00e0ff; padding-left: 10px; font-size: 1.1rem; }

    /* Buttons */
    .stButton button {
        width: 100%;
        background: rgba(0, 224, 255, 0.1);
        border: 1px solid #00e0ff;
        color: #00e0ff;
        font-family: 'Orbitron', sans-serif;
    }
    .stButton button:hover {
        background: #00e0ff;
        color: #000;
        box-shadow: 0 0 20px #00e0ff;
    }
</style>
""", unsafe_allow_html=True)

# --- LAYOUT CONSTRUCTION ---

# Top Bar
c1, c2, c3 = st.columns([1, 4, 1])
with c1:
    st.markdown(f"<div style='color:#00e0ff; font-family:Orbitron;'>SYS: ONLINE</div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div style='text-align:right; color:#88c0d0;'>{curr_time} | {curr_date}</div>", unsafe_allow_html=True)

st.divider()

col1, col2, col3 = st.columns([1, 1.5, 1])

# === LEFT PANEL: STATUS ===
with col1:
    st.markdown(f"""
    <div class="glass-card">
        <h4 style="color:#00e0ff; margin-top:0;">DIAGNOSTICS</h4>
        <p>CPU LOAD: <span style="color:#ff5555">{cpu}%</span></p>
        <div style="height:5px; background:#111; width:100%; margin-bottom:10px;"><div style="height:100%; width:{cpu}%; background:#ff5555;"></div></div>
        
        <p>RAM USAGE: <span style="color:#55ff55">{ram}%</span></p>
        <div style="height:5px; background:#111; width:100%; margin-bottom:10px;"><div style="height:100%; width:{ram}%; background:#55ff55;"></div></div>
        
        <br>
        <h4 style="color:#00e0ff;">ENVIRONMENT</h4>
        <p style="font-size:24px; margin:0;">{temp}°C</p>
        <small style="color:#aaa">Humidity: {hum}% | Wind: {wind}km/h</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("") # Spacer
    if st.button("CLEAR LOGS"):
        st.session_state['history'] = []
        st.rerun()

# === CENTER PANEL: INTERFACE ===
with col2:
    # Reactor Graphic
    st.markdown('<div class="reactor"></div>', unsafe_allow_html=True)
    
    # Mic Interaction
    st.markdown("<div style='text-align:center; color:#00e0ff; letter-spacing:2px; margin-bottom:10px;'>VOICE INTERFACE</div>", unsafe_allow_html=True)
    
    # The Mic Button Logic
    if st.button("🎙️ ACTIVATE MICROPHONE"):
        with st.spinner("Listening..."):
            text = listen_input()
            if text:
                st.session_state['last_command'] = text
                response = processcommand(text)
                st.session_state['history'].append((text, response))
                st.rerun()
            else:
                st.warning("No audio detected. Check your mic.")

    # Text Input Fallback
    def submit():
        txt = st.session_state.txt_input
        if txt:
            response = processcommand(txt)
            st.session_state['history'].append((txt, response))
            st.session_state.txt_input = ""
    
    st.text_input("MANUAL OVERRIDE", key="txt_input", on_change=submit, placeholder="Type command here...")

# === RIGHT PANEL: LOGS ===
with col3:
    st.markdown('<div class="glass-card" style="height: 65vh;">', unsafe_allow_html=True)
    st.markdown('<h4 style="color:#00e0ff; margin-top:0;">COMMUNICATION LOG</h4>', unsafe_allow_html=True)
    
    # Chat History inside a scrollable container
    chat_html = '<div class="chat-container">'
    # Iterate backwards so newest is at top (or manage via flex-direction)
    for q, a in reversed(st.session_state['history']):
        chat_html += f'<div class="msg-user">CMD: {q}</div>'
        chat_html += f'<div class="msg-ai">>> {a}</div><hr style="border-color:#112;">'
    chat_html += '</div>'
    
    st.markdown(chat_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)