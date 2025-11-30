import streamlit as st
import time
import datetime
from Project_core import processcommand, listen_input, get_system_stats, get_weather

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="J.A.R.V.I.S",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- LOAD DATA ---
cpu_usage, ram_usage, disk_usage = get_system_stats()
temp, humidity, wind = get_weather()
current_time = datetime.datetime.now().strftime("%H:%M:%S")
current_date = datetime.datetime.now().strftime("%B %d, %Y")

if 'start_time' not in st.session_state:
    st.session_state['start_time'] = time.time()
if 'command_count' not in st.session_state:
    st.session_state['command_count'] = 0
if 'history' not in st.session_state:
    st.session_state['history'] = [{"role": "jarvis", "text": "J.A.R.V.I.S backend online. How can I assist you, sir?"}]
if 'txt_input' not in st.session_state:
    st.session_state['txt_input'] = ""

# --- CALCULATE UPTIME ---
elapsed_time = int(time.time() - st.session_state['start_time'])
uptime_str = str(datetime.timedelta(seconds=elapsed_time))

# --- CSS STYLING (THE J.A.R.V.I.S LOOK) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&family=Roboto+Mono:wght@400&display=swap');

    /* GENERAL SETTINGS */
    .stApp {
        background-color: #020617;
        color: #00e0ff;
        font-family: 'Orbitron', sans-serif;
    }
    
    /* REMOVE DEFAULT PADDING */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }

    /* CARDS (PANELS) */
    .jarvis-card {
        background: rgba(10, 20, 35, 0.7);
        border: 1px solid #004d61;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 0 10px rgba(0, 224, 255, 0.1);
        backdrop-filter: blur(5px);
    }
    
    /* HEADERS */
    h3, h4, h5 {
        color: #00e0ff;
        text-transform: uppercase;
        margin: 0;
        padding-bottom: 10px;
        font-size: 14px;
        letter-spacing: 2px;
        border-bottom: 1px solid rgba(0, 224, 255, 0.3);
        margin-bottom: 10px;
    }

    /* STATS BARS */
    .stat-label { font-size: 12px; color: #88c0d0; display: flex; justify-content: space-between; }
    .progress-bg { background: #0d1b2a; height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 10px; }
    .progress-fill { background: #00e0ff; height: 100%; box-shadow: 0 0 10px #00e0ff; }

    /* ARC REACTOR (CENTER) */
    .reactor-container {
        display: flex; justify-content: center; align-items: center; height: 400px; flex-direction: column;
    }
    .reactor {
        width: 200px; height: 200px; border-radius: 50%;
        border: 10px solid rgba(0, 224, 255, 0.1);
        position: relative;
        display: flex; justify-content: center; align-items: center;
        box-shadow: 0 0 50px rgba(0, 224, 255, 0.2);
    }
    .reactor-inner {
        width: 140px; height: 140px; border-radius: 50%;
        border: 5px solid #00e0ff;
        box-shadow: 0 0 30px #00e0ff, inset 0 0 30px #00e0ff;
        animation: pulse 2s infinite ease-in-out;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.05); opacity: 1; box-shadow: 0 0 50px #00e0ff; }
        100% { transform: scale(0.95); opacity: 0.8; }
    }

    /* CHAT BUBBLES */
    .chat-box { height: 600px; overflow-y: auto; display: flex; flex-direction: column-reverse; }
    .bubble { padding: 10px 15px; border-radius: 10px; margin-bottom: 10px; font-family: 'Roboto Mono', monospace; font-size: 14px; max-width: 80%; }
    .bubble-jarvis { background: rgba(0, 224, 255, 0.1); border-left: 3px solid #00e0ff; align-self: flex-start; }
    .bubble-user { background: rgba(0, 255, 100, 0.1); border-right: 3px solid #00ff66; align-self: flex-end; text-align: right; color: #ccffdd; }
    
    /* BUTTONS */
    .stButton>button {
        width: 100%; border: 1px solid #00e0ff; background: transparent; color: #00e0ff;
        font-family: 'Orbitron'; transition: 0.3s;
    }
    .stButton>button:hover { background: rgba(0, 224, 255, 0.2); box-shadow: 0 0 15px #00e0ff; }
    
</style>
""", unsafe_allow_html=True)

# --- TOP HEADER ROW ---
top1, top2, top3 = st.columns([1, 2, 1])
with top1:
    st.markdown("## J.A.R.V.I.S <span style='font-size:12px; color:#0f0'>● ONLINE</span>", unsafe_allow_html=True)
with top2:
    st.markdown(f"<div style='text-align:center; font-size: 20px;'>{current_time} | {current_date}</div>", unsafe_allow_html=True)
with top3:
    st.markdown(f"<div style='text-align:right; font-size: 18px;'>📍 {temp}°C</div>", unsafe_allow_html=True)

st.write("---")

# --- MAIN LAYOUT (3 COLUMNS) ---
col_left, col_center, col_right = st.columns([1, 1.5, 1])

# === LEFT PANEL: DASHBOARD ===
with col_left:
    # 1. System Stats
    st.markdown("""
    <div class="jarvis-card">
        <h3>System Stats</h3>
        <div class="stat-label"><span>CPU Load</span><span>""" + str(cpu_usage) + """%</span></div>
        <div class="progress-bg"><div class="progress-fill" style="width: """ + str(cpu_usage) + """%;"></div></div>
        
        <div class="stat-label"><span>RAM Usage</span><span>""" + str(ram_usage) + """%</span></div>
        <div class="progress-bg"><div class="progress-fill" style="width: """ + str(ram_usage) + """%;"></div></div>
        
        <div class="stat-label"><span>Disk Space</span><span>""" + str(disk_usage) + """%</span></div>
        <div class="progress-bg"><div class="progress-fill" style="width: """ + str(disk_usage) + """%;"></div></div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Weather
    st.markdown(f"""
    <div class="jarvis-card">
        <h3>Weather</h3>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size: 40px;">☁️</div>
            <div style="text-align:right;">
                <div style="font-size: 30px;">{temp}°C</div>
                <div style="color: #88c0d0;">Humidity: {humidity}%</div>
                <div style="color: #88c0d0;">Wind: {wind} km/h</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Camera (Placeholder functionality as shown in image)
    with st.expander("📷 CAMERA FEED", expanded=True):
        cam_on = st.checkbox("Activate Camera")
        if cam_on:
            st.camera_input("Scanner", label_visibility="hidden")
        else:
            st.markdown("<div style='height:100px; background:#000; color:#555; display:flex; justify-content:center; align-items:center;'>Camera Offline</div>", unsafe_allow_html=True)

    # 4. Uptime
    st.markdown(f"""
    <div class="jarvis-card">
        <h3>System Uptime</h3>
        <div style="font-size: 24px; text-align:center; font-family:'Roboto Mono';">{uptime_str}</div>
        <div style="display:flex; justify-content:space-between; margin-top:10px; font-size:12px; color:#88c0d0;">
            <span>Session: 1</span>
            <span>Cmds: {st.session_state['command_count']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# === CENTER PANEL: CORE ===
with col_center:
    st.markdown("""
    <div class="reactor-container">
        <div class="reactor">
            <div class="reactor-inner"></div>
        </div>
        <h1 style="margin-top: 30px; letter-spacing: 10px; font-size: 40px;">J.A.R.V.I.S</h1>
        <div style="background: rgba(0, 224, 255, 0.1); padding: 5px 20px; border-radius: 20px; border: 1px solid #00e0ff; margin-top: 10px;">
            ● Listening for wake word...
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Action Buttons
    c1, c2, c3 = st.columns(3)
    with c2:
        if st.button("🎙️ SPEAK"):
            cmd = listen_input()
            if cmd:
                st.session_state['history'].append({"role": "user", "text": cmd})
                st.session_state['command_count'] += 1
                
                resp = processcommand(cmd)
                
                st.session_state['history'].append({"role": "jarvis", "text": resp})
                st.rerun()


# === RIGHT PANEL: CONVERSATION ===
with col_right:
    st.markdown("<h3>Conversation</h3>", unsafe_allow_html=True)
    
    # Chat History Container
    with st.container():
        for msg in st.session_state['history']:
            with st.chat_message(msg["role"]):
                st.write(msg["text"])

    # Input at bottom
    def submit_text():
        txt = st.session_state.get('txt_input', '')
        if txt:
            st.session_state['history'].append({"role": "user", "text": txt})
            st.session_state['command_count'] += 1
            resp = processcommand(txt)
            if resp:
                st.session_state['history'].append({"role": "jarvis", "text": resp})
            st.session_state.txt_input = ""
    st.text_input("Type a message...", key="txt_input", on_change=submit_text)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Clear Log"):
            st.session_state['history'] = []
            st.rerun()
    with c2:
        if st.button("News"):
            headlines = get_news()
            st.session_state['history'].append({"role": "jarvis", "text": "Here are the top headlines: \n" + "\n".join(headlines)})
            st.rerun()