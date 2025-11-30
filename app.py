import streamlit as st
import time
import datetime
import os
import pandas as pd
import yt_dlp
import tkinter as tk
from tkinter import filedialog
from Project_core import processcommand, listen_input, get_system_stats, get_weather

# --- IMPORT MODULES ---
# Make sure email_module.py and messaging_module.py are in the same folder
from email_module import EmailAssistant
from messaging_module import MessagingAssistant

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ARMOR AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INITIALIZE SINGLETONS (Background Services) ---

# 1. Email Bot (Session State)
if 'email_bot' not in st.session_state:
    st.session_state.email_bot = EmailAssistant()

# 2. Messaging Bot (Global Resource Cache)
# We use cache_resource because it runs background threads (scheduler/telegram bot)
# and we don't want to restart threads on every interaction.
@st.cache_resource
def get_messaging_bot():
    return MessagingAssistant()

msg_bot = get_messaging_bot()

# --- CUSTOM CSS STYLING (THEME ENGINE) ---
st.markdown("""
<style>
    /* IMPORT FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;400;600&display=swap');

    /* --- GLOBAL APP STYLES --- */
    .stApp {
        background-color: #050a14;
        background-image: radial-gradient(circle at 50% 50%, #0a1128 0%, #02040a 100%);
        color: #e0f7fa;
        font-family: 'Rajdhani', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Orbitron', sans-serif;
        color: #00e0ff;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 0 0 10px rgba(0, 224, 255, 0.5);
    }

    /* --- SIDEBAR STYLING --- */
    [data-testid="stSidebar"] {
        background-color: rgba(5, 10, 20, 0.95);
        border-right: 1px solid rgba(0, 224, 255, 0.2);
    }
    
    /* --- GLASSMORPHISM CARDS --- */
    .armor-card {
        background: rgba(13, 22, 35, 0.6);
        border: 1px solid rgba(0, 224, 255, 0.15);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .armor-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 20px rgba(0, 224, 255, 0.2);
        border-color: rgba(0, 224, 255, 0.4);
    }

    /* --- REACTOR ANIMATION (VOICE CORE) --- */
    .reactor-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px;
        position: relative;
    }
    .reactor {
        width: 140px;
        height: 140px;
        background: radial-gradient(circle, #00e0ff 0%, transparent 70%);
        border-radius: 50%;
        border: 4px solid rgba(0, 224, 255, 0.3);
        box-shadow: 0 0 30px #00e0ff, inset 0 0 30px #00e0ff;
        animation: pulse 3s infinite ease-in-out;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .reactor-core {
        width: 80px;
        height: 80px;
        background: #fff;
        border-radius: 50%;
        box-shadow: 0 0 50px #00e0ff;
        animation: flicker 0.1s infinite alternate;
        opacity: 0.9;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 20px #00e0ff; opacity: 0.7; }
        50% { transform: scale(1.05); box-shadow: 0 0 60px #00e0ff; opacity: 1; }
        100% { transform: scale(0.95); box-shadow: 0 0 20px #00e0ff; opacity: 0.7; }
    }
    @keyframes flicker {
        0% { opacity: 0.8; }
        100% { opacity: 1; }
    }

    /* --- CUSTOM BUTTONS --- */
    .stButton > button {
        background: rgba(0, 224, 255, 0.05);
        border: 1px solid #00e0ff;
        color: #00e0ff;
        font-family: 'Orbitron', sans-serif;
        border-radius: 4px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton > button:hover {
        background: rgba(0, 224, 255, 0.2);
        box-shadow: 0 0 15px #00e0ff;
        color: #fff;
    }
    .stButton > button:active {
        transform: scale(0.98);
    }

    /* --- INPUT FIELDS --- */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(10, 20, 30, 0.8);
        border: 1px solid rgba(0, 224, 255, 0.3);
        color: #fff;
        font-family: 'Rajdhani', sans-serif;
        border-radius: 4px;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #00e0ff;
        box-shadow: 0 0 10px rgba(0, 224, 255, 0.3);
    }

    /* --- CHAT BUBBLES --- */
    .chat-container {
        height: 55vh;
        overflow-y: auto;
        padding: 10px;
        display: flex;
        flex-direction: column-reverse;
        scroll-behavior: smooth;
    }
    .bubble {
        padding: 12px 18px;
        border-radius: 12px;
        margin-bottom: 12px;
        max-width: 80%;
        font-size: 1.1rem;
        line-height: 1.5;
        position: relative;
        animation: fadeIn 0.3s ease-out;
    }
    .bubble-user {
        background: rgba(0, 255, 136, 0.1);
        border-right: 3px solid #00ff88;
        align-self: flex-end;
        text-align: right;
        color: #ccffdd;
        margin-left: auto;
    }
    .bubble-ai {
        background: rgba(0, 224, 255, 0.1);
        border-left: 3px solid #00e0ff;
        align-self: flex-start;
        text-align: left;
        color: #d1f7ff;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* --- SCROLLBAR --- */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #050a14; }
    ::-webkit-scrollbar-thumb { background: #00e0ff; border-radius: 4px; }

    /* --- UTILITY CLASSES --- */
    .status-active { color: #00ff88; text-shadow: 0 0 5px #00ff88; }
    .status-warn { color: #ffcc00; text-shadow: 0 0 5px #ffcc00; }
    .status-err { color: #ff3333; text-shadow: 0 0 5px #ff3333; }
    
    .stat-label { font-size: 0.9rem; color: #88c0d0; text-transform: uppercase; }
    .stat-val { font-size: 1.5rem; font-weight: bold; font-family: 'Orbitron'; color: #fff; }
    
    /* Progress Bar Hack */
    .stProgress > div > div > div > div {
        background-color: #00e0ff;
        box-shadow: 0 0 10px #00e0ff;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def open_folder_dialog():
    """Opens local folder picker dialog."""
    root = tk.Tk()
    root.withdraw() 
    root.wm_attributes('-topmost', 1) 
    folder_path = filedialog.askdirectory(master=root)
    root.destroy()
    return folder_path

def render_stat_card(label, value, color="#00e0ff"):
    return f"""
    <div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:8px; border-left: 3px solid {color}; margin-bottom:10px;">
        <div class="stat-label">{label}</div>
        <div class="stat-val" style="color:{color}">{value}</div>
    </div>
    """

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<div style='text-align: center; margin-bottom: 20px;'><h1 style='font-size: 2em; margin:0;'>ARMOR</h1><small style='color:#00e0ff; letter-spacing:3px;'>SYSTEMS ONLINE</small></div>", unsafe_allow_html=True)
    
    st.markdown("### NAVIGATION")
    mode = st.radio(
        "Select Module", 
        ["🎙️ COMMAND CENTER", "📥 DOWNLOADER", "✉️ EMAIL PROTOCOL", "💬 MESSAGING"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Minimal System Stats in Sidebar
    cpu, ram, disk = get_system_stats()
    st.markdown(f"**SYS DIAGNOSTICS**", unsafe_allow_html=True)
    st.markdown(f"<small>CPU LOAD</small>", unsafe_allow_html=True)
    st.progress(cpu / 100)
    st.markdown(f"<small>RAM USAGE</small>", unsafe_allow_html=True)
    st.progress(ram / 100)
    
    st.divider()
    st.markdown("<div style='text-align:center; color:#666; font-size:10px;'>ARMOR AI v5.0<br>SECURE CONNECTION</div>", unsafe_allow_html=True)

# --- HEADER SECTION ---
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown(f"## {mode}")
with col_head2:
    curr_time = datetime.datetime.now().strftime("%H:%M:%S")
    curr_date = datetime.datetime.now().strftime("%a, %d %b %Y")
    st.markdown(f"""
    <div style='text-align:right; font-family:"Orbitron"; color:#00e0ff;'>
        <div style="font-size:1.5em;">{curr_time}</div>
        <div style="font-size:0.8em; color:#88c0d0;">{curr_date}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("") # Spacer

# ==========================================
# MODULE 1: J.A.R.V.I.S COMMAND CENTER
# ==========================================
if mode == "🎙️ COMMAND CENTER":
    if 'history' not in st.session_state: st.session_state['history'] = []
    
    # Layout: Left (Reactor/Controls) | Right (Chat Log/Info)
    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        # Reactor Visual
        st.markdown('<div class="armor-card"><div class="reactor-container"><div class="reactor"><div class="reactor-core"></div></div></div></div>', unsafe_allow_html=True)
        
        # Status
        temp, hum, wind = get_weather()
        st.markdown(f"""
        <div class="armor-card">
            <div style="display:flex; justify-content:space-between;">
                {render_stat_card("TEMP", f"{temp}°C", "#ffcc00")}
                {render_stat_card("HUMIDITY", f"{hum}%", "#00ff88")}
                {render_stat_card("WIND", f"{wind} km/h", "#00e0ff")}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Controls
        st.markdown('<div class="armor-card">', unsafe_allow_html=True)
        st.markdown("#### VOICE INPUT")
        if st.button("🎙️ INITIATE LISTENING SEQUENCE", use_container_width=True):
            with st.spinner("LISTENING..."):
                text = listen_input()
                if text:
                    response = processcommand(text)
                    st.session_state['history'].append((text, response))
                    st.rerun()
                else:
                    st.warning("NO AUDIO DETECTED")
        
        st.markdown("#### MANUAL OVERRIDE")
        def submit():
            txt = st.session_state.txt_input
            if txt:
                response = processcommand(txt)
                st.session_state['history'].append((txt, response))
                st.session_state.txt_input = ""
        
        st.text_input("ENTER COMMAND", key="txt_input", on_change=submit, placeholder="Type command here...")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("PURGE LOGS"):
            st.session_state['history'] = []
            st.rerun()

    with c2:
        st.markdown('<div class="armor-card" style="height: 70vh;">', unsafe_allow_html=True)
        st.markdown("#### COMMUNICATION LOG")
        
        # Custom HTML Chat Render
        chat_html = '<div class="chat-container">'
        for q, a in reversed(st.session_state['history']):
            chat_html += f'<div class="bubble bubble-user">{q}</div>'
            chat_html += f'<div class="bubble bubble-ai">{a}</div>'
        chat_html += '</div>'
        
        st.markdown(chat_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# MODULE 2: YOUTUBE DOWNLOADER
# ==========================================
elif mode == "📥 DOWNLOADER":
    c_main = st.container()
    
    with c_main:
        st.markdown('<div class="armor-card">', unsafe_allow_html=True)
        col_input, col_opt = st.columns([2, 1])
        
        with col_input:
            video_url = st.text_input("TARGET URL (YouTube)", placeholder="https://youtube.com/watch?v=...")
        
        with col_opt:
            format_type = st.selectbox("FORMAT TYPE", ["Video + Audio", "Audio Only (MP3)"])
        
        c_res, c_path = st.columns([1, 2])
        with c_res:
            if format_type == "Video + Audio":
                resolution = st.selectbox("RESOLUTION", ["Best Available", "1080p", "720p", "480p"])
            else:
                resolution = st.selectbox("BITRATE", ["Best Quality (320kbps)", "Standard (128kbps)"])
        
        with c_path:
            if 'download_path' not in st.session_state:
                st.session_state['download_path'] = os.getcwd()
            
            c_p_text, c_p_btn = st.columns([3, 1])
            with c_p_text:
                st.text_input("OUTPUT PATH", value=st.session_state['download_path'], disabled=True, label_visibility="collapsed")
            with c_p_btn:
                if st.button("📂 BROWSE"):
                    path = open_folder_dialog()
                    if path: 
                        st.session_state['download_path'] = path
                        st.rerun()

        st.write("")
        if st.button("INITIATE DOWNLOAD SEQUENCE", type="primary", use_container_width=True):
            if video_url:
                status_box = st.empty()
                prog_bar = st.progress(0)
                
                try:
                    status_box.info("ANALYZING METADATA...")
                    
                    def progress_hook(d):
                        if d['status'] == 'downloading':
                            try:
                                p = d.get('_percent_str', '0%').replace('%','')
                                prog_bar.progress(float(p) / 100)
                                status_box.markdown(f"<span style='color:#00e0ff'>DOWNLOADING:</span> {d.get('_percent_str')} | SPEED: {d.get('_speed_str')}", unsafe_allow_html=True)
                            except: pass
                        if d['status'] == 'finished':
                            prog_bar.progress(100)
                            status_box.success("DOWNLOAD COMPLETE. PROCESSING...")

                    ydl_opts = {
                        'outtmpl': f"{st.session_state['download_path']}/%(title)s.%(ext)s",
                        'progress_hooks': [progress_hook],
                        'quiet': True,
                        'no_warnings': True,
                    }

                    if format_type == "Audio Only (MP3)":
                        ydl_opts['format'] = 'bestaudio/best'
                        ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192',}]
                    else:
                        if resolution == "Best Available": ydl_opts['format'] = 'bestvideo+bestaudio/best'
                        elif resolution == "1080p": ydl_opts['format'] = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
                        elif resolution == "720p": ydl_opts['format'] = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
                        elif resolution == "480p": ydl_opts['format'] = 'bestvideo[height<=480]+bestaudio/best[height<=480]'

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video_url])
                    st.balloons()
                    status_box.success(f"FILE SECURED AT: {st.session_state['download_path']}")
                except Exception as e:
                    status_box.error(f"DOWNLOAD ERROR: {str(e)}")
            else:
                st.warning("INVALID TARGET URL")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# MODULE 3: EMAIL PROTOCOL
# ==========================================
elif mode == "✉️ EMAIL PROTOCOL":
    if 'email_draft' not in st.session_state:
        st.session_state['email_draft'] = {"to": "", "subject": "", "body": ""}

    # Styled Tabs
    tab1, tab2, tab3 = st.tabs(["COMPOSE", "INBOX", "CONTACTS"])

    with tab1:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown('<div class="armor-card">', unsafe_allow_html=True)
            st.markdown("#### VOICE COMMAND")
            st.info("Example: 'Send an email to John about the project'")
            if st.button("🎙️ DICTATE", use_container_width=True):
                with st.spinner("LISTENING..."):
                    cmd = listen_input()
                    if cmd:
                        parsed = st.session_state.email_bot.parse_voice_command(cmd)
                        if parsed:
                            st.session_state['email_draft']['to'] = parsed.get('recipient_email') or parsed.get('recipient_name') or ""
                            st.session_state['email_draft']['subject'] = parsed.get('subject') or ""
                            st.session_state['email_draft']['body'] = parsed.get('body') or ""
                            st.rerun()
                        else: st.error("PARSING FAILED")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with c2:
            st.markdown('<div class="armor-card">', unsafe_allow_html=True)
            to_addr = st.text_input("RECIPIENT", value=st.session_state['email_draft']['to'], placeholder="target@domain.com")
            
            c_sub, c_gen = st.columns([3, 1])
            with c_sub:
                subj = st.text_input("SUBJECT", value=st.session_state['email_draft']['subject'])
            with c_gen:
                st.write("")
                st.write("")
                if st.button("✨ AUTO-GEN"):
                    if subj:
                        with st.spinner("GENERATING..."):
                            body_gen = st.session_state.email_bot.generate_email_body(subj)
                            st.session_state['email_draft']['body'] = body_gen
                            st.rerun()
            
            body = st.text_area("BODY", value=st.session_state['email_draft']['body'], height=200)
            
            # Sync state
            st.session_state['email_draft'].update({"to": to_addr, "subject": subj, "body": body})
            
            if st.button("TRANSMIT MESSAGE", type="primary", use_container_width=True):
                if to_addr and body:
                    with st.spinner("ENCRYPTING AND SENDING..."):
                        success, msg = st.session_state.email_bot.send_email(to_addr, subj, body)
                        if success:
                            st.success(msg)
                            st.balloons()
                            st.session_state['email_draft'] = {"to": "", "subject": "", "body": ""}
                        else: st.error(msg)
                else: st.warning("MISSING PARAMETERS")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="armor-card">', unsafe_allow_html=True)
        if st.button("🔄 SYNCHRONIZE INBOX"):
            with st.spinner("FETCHING DATA..."):
                emails = st.session_state.email_bot.fetch_recent_emails(limit=5)
                if emails:
                    for e in emails:
                        st.markdown(f"""
                        <div style="border-bottom:1px solid #333; padding:10px 0;">
                            <strong style="color:#00ff88">{e['sender']}</strong><br>
                            <span style="color:#00e0ff">{e['subject']}</span><br>
                            <small style="color:#aaa">{e['preview']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else: st.info("INBOX EMPTY OR DISCONNECTED")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="armor-card">', unsafe_allow_html=True)
        col_add, col_list = st.columns(2)
        with col_add:
            st.markdown("#### ADD CONTACT")
            n = st.text_input("Name")
            e = st.text_input("Email")
            if st.button("SAVE CONTACT"):
                if n and e:
                    res = st.session_state.email_bot.add_contact(n, e)
                    st.success(res)
                    st.rerun()
        with col_list:
            st.markdown("#### DIRECTORY")
            contacts = st.session_state.email_bot.load_contacts()
            if contacts:
                for c in contacts:
                    st.markdown(f"`{c['name'].upper()}` : {c['email']}")
            else: st.info("DATABASE EMPTY")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# MODULE 4: MESSAGING
# ==========================================
elif mode == "💬 MESSAGING":
    tab1, tab2, tab3, tab4 = st.tabs(["SEND", "FEED", "LOGS", "CONFIG"])

    with tab1:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown('<div class="armor-card">', unsafe_allow_html=True)
            st.markdown("#### VOICE COMMAND")
            st.info("Ex: 'Send WhatsApp to Mom saying I am safe'")
            if st.button("🎙️ DICTATE", use_container_width=True):
                with st.spinner("PROCESSING..."):
                    cmd = listen_input()
                    if cmd:
                        parsed = msg_bot.parse_command(cmd)
                        if parsed:
                            if parsed['intent'] == 'send':
                                contact = msg_bot.get_contact(parsed.get('recipient_name', ''))
                                if not contact: st.error("CONTACT NOT FOUND")
                                else:
                                    if parsed['platform'] == 'whatsapp' and contact.get('phone'):
                                        ok, m = msg_bot.send_whatsapp(contact['phone'], parsed['message_body'])
                                        st.success(m) if ok else st.error(m)
                                    elif parsed['platform'] == 'telegram' and contact.get('telegram_id'):
                                        ok, m = msg_bot.send_telegram(contact['telegram_id'], parsed['message_body'])
                                        st.success(m) if ok else st.error(m)
                            elif parsed['intent'] == 'schedule':
                                contact = msg_bot.get_contact(parsed.get('recipient_name', ''))
                                if contact:
                                    msg_bot.schedule_message(parsed['platform'], contact, parsed['message_body'], parsed['schedule_time'])
                                    st.success(f"SCHEDULED: {parsed['schedule_time']}")
                                else: st.error("CONTACT NOT FOUND")
                        else: st.error("INTENT UNRECOGNIZED")
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="armor-card">', unsafe_allow_html=True)
            st.markdown("#### MANUAL CONSOLE")
            m_plat = st.selectbox("PLATFORM", ["WhatsApp", "Telegram"])
            c_names = [c['name'] for c in msg_bot.contacts]
            m_cont = st.selectbox("CONTACT", c_names if c_names else ["No contacts"])
            m_body = st.text_area("MESSAGE")
            
            do_sched = st.checkbox("SCHEDULE TRANSMISSION")
            m_time = None
            if do_sched:
                cd, ct = st.columns(2)
                d = cd.date_input("Date")
                t = ct.time_input("Time")
                m_time = datetime.datetime.combine(d, t).isoformat()
            
            if st.button("EXECUTE", type="primary", use_container_width=True):
                c_data = msg_bot.get_contact(m_cont)
                if not c_data: st.error("INVALID CONTACT")
                else:
                    if do_sched:
                        msg_bot.schedule_message(m_plat.lower(), c_data, m_body, m_time)
                        st.success("TRANSMISSION SCHEDULED")
                    else:
                        if m_plat == "WhatsApp":
                            ok, txt = msg_bot.send_whatsapp(c_data.get('phone'), m_body)
                        else:
                            ok, txt = msg_bot.send_telegram(c_data.get('telegram_id'), m_body)
                        st.success(txt) if ok else st.error(txt)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="armor-card">', unsafe_allow_html=True)
        col_h, col_r = st.columns([4, 1])
        col_h.markdown("#### LIVE TELEGRAM FEED")
        if col_r.button("REFRESH"): st.rerun()
        
        if msg_bot.incoming_log:
            for item in msg_bot.incoming_log:
                s_color = "#6c757d"
                if item['analysis']['sentiment'] == 'positive': s_color = "#28a745"
                elif item['analysis']['sentiment'] == 'negative': s_color = "#dc3545"
                
                st.markdown(f"""
                <div style="background:rgba(0,0,0,0.3); padding:15px; border-radius:8px; margin-bottom:10px; border-left:3px solid {s_color}">
                    <div style="display:flex; justify-content:space-between;">
                        <strong style="color:#00ff99">{item['sender']}</strong>
                        <small style="color:#aaa">{item['time']}</small>
                    </div>
                    <p style="margin:5px 0;">"{item['text']}"</p>
                    <div style="font-size:0.8em; color:#88c0d0; margin-top:5px;">
                        DETECTED: <span style="color:{s_color}">{item['analysis']['emotion'].upper()}</span> | 
                        SUGGESTION: <em>{item['suggested_reply']}</em>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"SEND REPLY TO {item['sender']}", key=f"rep_{item['time']}"):
                    msg_bot.send_telegram(item['id'], item['suggested_reply'])
                    st.success("REPLY SENT")
        else: st.info("NO DATA STREAM")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="armor-card">', unsafe_allow_html=True)
        st.markdown("#### AUTO-REPLY LOGS")
        if msg_bot.auto_reply_history:
            st.dataframe(pd.DataFrame(msg_bot.auto_reply_history), use_container_width=True)
        else: st.caption("NO ACTIVITY RECORDED")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="armor-card">', unsafe_allow_html=True)
        st.markdown("#### PROTOCOL SETTINGS")
        c1, c2 = st.columns(2)
        with c1:
            msg_bot.sentiment_analysis_enabled = st.toggle("SENTIMENT ANALYSIS", value=True)
        with c2:
            msg_bot.global_auto_reply = st.toggle("GLOBAL AUTO-REPLY", value=False)
            if msg_bot.global_auto_reply: st.warning("WARNING: AUTONOMOUS MODE ACTIVE")
        
        st.markdown("#### PENDING SCHEDULE")
        if msg_bot.scheduled_messages:
            st.dataframe(pd.DataFrame(msg_bot.scheduled_messages), use_container_width=True)
        else: st.caption("QUEUE EMPTY")
        st.markdown('</div>', unsafe_allow_html=True)