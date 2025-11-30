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

# --- CUSTOM CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500&display=swap');
    
    /* General App Styling */
    .stApp { background-color: #050a14; font-family: 'Rajdhani', sans-serif; overflow-x: hidden; }
    header, footer {visibility: hidden;}
    [data-testid="stSidebar"] { background-color: #0b1221; border-right: 1px solid #00e0ff33; }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(13, 22, 35, 0.7);
        border: 1px solid rgba(0, 224, 255, 0.2);
        box-shadow: 0 0 15px rgba(0, 224, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        color: #e0f7fa;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
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
    
    /* Chat & Logs */
    .chat-container { height: 60vh; overflow-y: auto; display: flex; flex-direction: column-reverse; padding-right: 10px; }
    
    /* Buttons & Inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] { 
        background-color: #0d1625; color: #00e0ff; border: 1px solid #00e0ff55; 
    }
    .stButton button { 
        width: 100%; background: rgba(0, 224, 255, 0.1); border: 1px solid #00e0ff; color: #00e0ff; font-family: 'Orbitron'; 
    }
    .stButton button:hover { background: #00e0ff; color: #000; box-shadow: 0 0 20px #00e0ff; }
    
    /* Sentiment Badges */
    .badge-pos { background-color: #28a745; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
    .badge-neg { background-color: #dc3545; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
    .badge-neu { background-color: #6c757d; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
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

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='color:#00e0ff; font-family:Orbitron;'>MENU</h2>", unsafe_allow_html=True)
    mode = st.selectbox("Select Interface", [
        "🎙️ J.A.R.V.I.S Assistant", 
        "📥 YouTube Downloader",
        "✉️ Email Protocol",
        "💬 Messaging Assistant"
    ])
    st.divider()
    st.markdown("<div style='color:#666; font-size:12px;'>ARMOR SYSTEMS v4.0</div>", unsafe_allow_html=True)

# --- TOP HEADER ---
curr_time = datetime.datetime.now().strftime("%H:%M")
curr_date = datetime.datetime.now().strftime("%a, %b %d")
c1, c2, c3 = st.columns([1, 4, 1])
with c1: st.markdown(f"<div style='color:#00e0ff; font-family:Orbitron;'>SYS: ONLINE</div>", unsafe_allow_html=True)
with c3: st.markdown(f"<div style='text-align:right; color:#88c0d0;'>{curr_time} | {curr_date}</div>", unsafe_allow_html=True)
st.divider()

# ==========================================
# MODE 1: J.A.R.V.I.S ASSISTANT (Core)
# ==========================================
if mode == "🎙️ J.A.R.V.I.S Assistant":
    if 'history' not in st.session_state: st.session_state['history'] = []
    
    # Live Data
    cpu, ram, disk = get_system_stats()
    temp, hum, wind = get_weather()

    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    # Left: Diagnostics
    with col1:
        st.markdown(f"""
        <div class="glass-card">
            <h4 style="color:#00e0ff; margin-top:0;">DIAGNOSTICS</h4>
            <p>CPU: <span style="color:#ff5555">{cpu}%</span></p>
            <div style="height:5px; background:#111; width:100%; margin-bottom:10px;"><div style="height:100%; width:{cpu}%; background:#ff5555;"></div></div>
            <p>RAM: <span style="color:#55ff55">{ram}%</span></p>
            <div style="height:5px; background:#111; width:100%; margin-bottom:10px;"><div style="height:100%; width:{ram}%; background:#55ff55;"></div></div>
            <br>
            <h4 style="color:#00e0ff;">ENV</h4>
            <p style="font-size:24px; margin:0;">{temp}°C</p>
            <small style="color:#aaa">H: {hum}% | W: {wind}km/h</small>
        </div>
        """, unsafe_allow_html=True)
        if st.button("CLEAR LOGS"):
            st.session_state['history'] = []
            st.rerun()

    # Center: Voice Interface
    with col2:
        st.markdown('<div class="reactor"></div>', unsafe_allow_html=True)
        st.markdown("<div style='text-align:center; color:#00e0ff; letter-spacing:2px; margin-bottom:10px;'>VOICE INTERFACE</div>", unsafe_allow_html=True)
        
        if st.button("🎙️ ACTIVATE MICROPHONE"):
            with st.spinner("Listening..."):
                text = listen_input()
                if text:
                    response = processcommand(text)
                    st.session_state['history'].append((text, response))
                    st.rerun()
                else:
                    st.warning("No audio detected.")

        def submit():
            txt = st.session_state.txt_input
            if txt:
                response = processcommand(txt)
                st.session_state['history'].append((txt, response))
                st.session_state.txt_input = ""
        st.text_input("MANUAL OVERRIDE", key="txt_input", on_change=submit, placeholder="Type command...")

    # Right: Logs
    with col3:
        st.markdown('<div class="glass-card" style="height: 65vh;">', unsafe_allow_html=True)
        st.markdown('<h4 style="color:#00e0ff; margin-top:0;">COMMUNICATION LOG</h4>', unsafe_allow_html=True)
        chat_html = '<div class="chat-container">'
        for q, a in reversed(st.session_state['history']):
            chat_html += f'<div class="msg-user">CMD: {q}</div><div class="msg-ai">>> {a}</div><hr style="border-color:#112;">'
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# MODE 2: YOUTUBE DOWNLOADER
# ==========================================
elif mode == "📥 YouTube Downloader":
    st.markdown("<h2 style='text-align:center; color:#00e0ff;'>SECURE DOWNLOAD PROTOCOL</h2>", unsafe_allow_html=True)
    d_col1, d_col2, d_col3 = st.columns([1, 2, 1])
    
    with d_col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        video_url = st.text_input("TARGET URL (YouTube)", placeholder="https://youtube.com/watch?v=...")
        format_type = st.radio("DOWNLOAD TYPE", ["Video + Audio", "Audio Only (MP3)"], horizontal=True)
        
        if format_type == "Video + Audio":
            resolution = st.selectbox("RESOLUTION", ["Best Available", "1080p", "720p", "480p", "360p"])
        else:
            resolution = st.selectbox("AUDIO QUALITY", ["Best Quality (320kbps)", "Standard (128kbps)"])

        col_path, col_btn = st.columns([3, 1])
        with col_path:
            if 'download_path' not in st.session_state:
                st.session_state['download_path'] = os.getcwd()
            st.text_input("SAVE LOCATION", value=st.session_state['download_path'], disabled=True)
        with col_btn:
            st.write("") 
            st.write("") 
            if st.button("📂"):
                selected_folder = open_folder_dialog()
                if selected_folder:
                    st.session_state['download_path'] = selected_folder
                    st.rerun()

        if st.button("INITIATE DOWNLOAD", type="primary"):
            if video_url:
                status_text = st.empty()
                progress_bar = st.progress(0)
                try:
                    status_text.info("Analyzing Metadata...")
                    def progress_hook(d):
                        if d['status'] == 'downloading':
                            try:
                                p = d.get('_percent_str', '0%').replace('%','')
                                progress_bar.progress(float(p) / 100)
                                status_text.info(f"Downloading: {d.get('_percent_str')} | Speed: {d.get('_speed_str')}")
                            except: pass
                        if d['status'] == 'finished':
                            progress_bar.progress(100)
                            status_text.success("Download Complete! Processing...")

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
                        elif resolution == "360p": ydl_opts['format'] = 'bestvideo[height<=360]+bestaudio/best[height<=360]'

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video_url])
                    st.balloons()
                    status_text.success(f"Saved to: {st.session_state['download_path']}")
                except Exception as e:
                    status_text.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter a valid URL.")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# MODE 3: EMAIL PROTOCOL
# ==========================================
elif mode == "✉️ Email Protocol":
    st.markdown("<h2 style='text-align:center; color:#00e0ff;'>SECURE COMMUNICATIONS LINK</h2>", unsafe_allow_html=True)
    
    # Init Email Draft
    if 'email_draft' not in st.session_state:
        st.session_state['email_draft'] = {"to": "", "subject": "", "body": ""}

    tab1, tab2, tab3 = st.tabs(["COMPOSE", "INBOX", "CONTACTS"])

    # --- COMPOSE ---
    with tab1:
        e_col1, e_col2 = st.columns([1, 2])
        
        with e_col1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Voice Command")
            st.info("Try: 'Send an email to John about the project'")
            
            if st.button("🎙️ DICTATE EMAIL"):
                with st.spinner("Listening..."):
                    cmd = listen_input()
                    if cmd:
                        st.success(f"Recognized: {cmd}")
                        parsed = st.session_state.email_bot.parse_voice_command(cmd)
                        if parsed:
                            st.session_state['email_draft']['to'] = parsed.get('recipient_email') or parsed.get('recipient_name') or ""
                            st.session_state['email_draft']['subject'] = parsed.get('subject') or ""
                            st.session_state['email_draft']['body'] = parsed.get('body') or ""
                            st.rerun()
                        else: st.error("Could not parse email intent.")
                    else: st.warning("No audio detected.")
            st.markdown('</div>', unsafe_allow_html=True)

        with e_col2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Secure Transmission Form")
            
            to_addr = st.text_input("RECIPIENT", value=st.session_state['email_draft']['to'], placeholder="name@example.com")
            
            # Subject and AI Generator
            col_sub, col_gen = st.columns([3, 1])
            with col_sub:
                subj = st.text_input("SUBJECT", value=st.session_state['email_draft']['subject'])
            with col_gen:
                st.write("") 
                st.write("") 
                if st.button("✨ AUTO-GEN", help="Generate email body from Subject"):
                    if subj:
                        with st.spinner("Generating..."):
                            body_gen = st.session_state.email_bot.generate_email_body(subj)
                            st.session_state['email_draft']['body'] = body_gen
                            st.rerun()
                    else: st.warning("Enter subject first.")

            body = st.text_area("BODY", value=st.session_state['email_draft']['body'], height=200)
            
            # Update State
            st.session_state['email_draft']['to'] = to_addr
            st.session_state['email_draft']['subject'] = subj
            st.session_state['email_draft']['body'] = body

            if st.button("SEND TRANSMISSION", type="primary"):
                if to_addr and body:
                    with st.spinner("Sending..."):
                        success, msg = st.session_state.email_bot.send_email(to_addr, subj, body)
                        if success:
                            st.success(msg)
                            st.balloons()
                            st.session_state['email_draft'] = {"to": "", "subject": "", "body": ""}
                        else: st.error(msg)
                else: st.warning("Fields required.")
            st.markdown('</div>', unsafe_allow_html=True)

    # --- INBOX ---
    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        if st.button("🔄 REFRESH INBOX"):
            with st.spinner("Fetching..."):
                emails = st.session_state.email_bot.fetch_recent_emails(limit=5)
                if emails:
                    for e in emails:
                        st.markdown(f"**From:** {e['sender']}")
                        st.markdown(f"**Subject:** {e['subject']}")
                        st.text(f"{e['preview']}")
                        st.divider()
                else: st.info("No new emails.")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- CONTACTS ---
    with tab3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            st.subheader("Add Contact")
            n = st.text_input("Name")
            e = st.text_input("Email")
            if st.button("SAVE"):
                if n and e:
                    res = st.session_state.email_bot.add_contact(n, e)
                    st.success(res)
                    st.rerun()
        with c_col2:
            st.subheader("Directory")
            contacts = st.session_state.email_bot.load_contacts()
            if contacts:
                for c in contacts: st.code(f"{c['name']}: {c['email']}")
            else: st.info("Empty.")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# MODE 4: MESSAGING ASSISTANT (NEW)
# ==========================================
elif mode == "💬 Messaging Assistant":
    st.markdown("<h2 style='text-align:center; color:#00e0ff;'>MESSAGING COMMAND CENTER</h2>", unsafe_allow_html=True)
    
    # Tabs for Messaging Features
    tab1, tab2, tab3, tab4 = st.tabs(["SEND / SCHEDULE", "INBOX (Telegram)", "AUTO-REPLY LOG", "CONFIG"])

    # --- TAB 1: SEND & SCHEDULE ---
    with tab1:
        col_voice, col_manual = st.columns([1, 2])
        
        with col_voice:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Voice Command")
            st.info("Example: 'Send a WhatsApp to Mom saying I will be late'")
            st.info("Example: 'Schedule a Telegram to Rohan tomorrow at 9 AM'")
            
            if st.button("🎙️ DICTATE COMMAND"):
                with st.spinner("Processing..."):
                    cmd = listen_input()
                    if cmd:
                        st.success(f"Heard: {cmd}")
                        parsed = msg_bot.parse_command(cmd)
                        
                        if parsed:
                            st.json(parsed) # Debug view
                            
                            # Intent: Send Immediately
                            if parsed['intent'] == 'send':
                                contact = msg_bot.get_contact(parsed.get('recipient_name', ''))
                                if not contact: 
                                    st.error(f"Contact '{parsed.get('recipient_name')}' not found.")
                                else:
                                    if parsed['platform'] == 'whatsapp' and contact.get('phone'):
                                        ok, m = msg_bot.send_whatsapp(contact['phone'], parsed['message_body'])
                                        if ok: st.success(m)
                                        else: st.error(m)
                                    elif parsed['platform'] == 'telegram' and contact.get('telegram_id'):
                                        ok, m = msg_bot.send_telegram(contact['telegram_id'], parsed['message_body'])
                                        if ok: st.success(m)
                                        else: st.error(m)
                                    else:
                                        st.error("Missing phone/ID for this platform.")
                            
                            # Intent: Schedule
                            elif parsed['intent'] == 'schedule':
                                contact = msg_bot.get_contact(parsed.get('recipient_name', ''))
                                if contact:
                                    msg_bot.schedule_message(
                                        parsed['platform'], 
                                        contact, 
                                        parsed['message_body'], 
                                        parsed['schedule_time']
                                    )
                                    st.success(f"Message Scheduled for {parsed['schedule_time']}")
                                else: st.error("Contact not found.")
                        else:
                            st.error("Could not understand the command.")
                    else:
                        st.warning("No audio detected.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_manual:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Manual Console")
            
            # Form
            m_platform = st.selectbox("Platform", ["WhatsApp", "Telegram"])
            # Contact List
            contact_names = [c['name'] for c in msg_bot.contacts]
            m_contact = st.selectbox("Contact", contact_names if contact_names else ["No contacts"])
            
            m_msg = st.text_area("Message Body")
            
            # Scheduling Options
            do_schedule = st.checkbox("Schedule for later")
            m_time = None
            if do_schedule:
                c1, c2 = st.columns(2)
                d = c1.date_input("Date")
                t = c2.time_input("Time")
                m_time = datetime.datetime.combine(d, t).isoformat()
            
            if st.button("EXECUTE OPERATION"):
                if not msg_bot.contacts:
                    st.error("Please add contacts in config/contacts.json first.")
                else:
                    contact_data = msg_bot.get_contact(m_contact)
                    if not contact_data: 
                        st.error("Invalid contact.")
                    else:
                        if do_schedule:
                            msg_bot.schedule_message(m_platform.lower(), contact_data, m_msg, m_time)
                            st.success("Message Scheduled.")
                        else:
                            if m_platform == "WhatsApp":
                                ok, txt = msg_bot.send_whatsapp(contact_data.get('phone'), m_msg)
                            else:
                                ok, txt = msg_bot.send_telegram(contact_data.get('telegram_id'), m_msg)
                            
                            if ok: st.success(txt)
                            else: st.error(txt)
            st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 2: INBOX & SENTIMENT ---
    with tab2:
        st.markdown("### Live Telegram Feed & Sentiment Analysis")
        # In a real deployment, we'd use st.empty() or streamlit-autorefresh.
        # Here we rely on a manual refresh button for simplicity.
        if st.button("REFRESH FEED"):
            st.rerun()
        
        if msg_bot.incoming_log:
            for item in msg_bot.incoming_log:
                # Color code sentiment
                s_color = "badge-neu"
                if item['analysis']['sentiment'] == 'positive': s_color = "badge-pos"
                elif item['analysis']['sentiment'] == 'negative': s_color = "badge-neg"
                
                with st.container():
                    st.markdown(f"""
                    <div class="glass-card" style="padding:15px; margin-bottom:15px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h4 style="margin:0; color:#00ff99;">{item['sender']}</h4>
                            <small style="color:#aaa;">{item['time']}</small>
                        </div>
                        <p style="margin:10px 0; font-size:1.1em;">"{item['text']}"</p>
                        <hr style="border-color:#333;">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span class="{s_color}">{item['analysis']['emotion'].upper()}</span>
                            <span style="color:#aaa;">AI Suggestion:</span>
                            <span style="color:#00e0ff; font-style:italic;">{item['suggested_reply']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # One-click reply
                    if st.button(f"Send Reply to {item['sender']}", key=f"rep_{item['time']}"):
                        msg_bot.send_telegram(item['id'], item['suggested_reply'])
                        st.success("Reply Sent.")
        else:
            st.info("No incoming messages logged yet. (Ensure Telegram Bot is running and receiving messages).")

    # --- TAB 3: LOGS ---
    with tab3:
        st.markdown("### Auto-Reply History")
        if msg_bot.auto_reply_history:
            df = pd.DataFrame(msg_bot.auto_reply_history)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No auto-replies have been triggered yet.")

    # --- TAB 4: CONFIG ---
    with tab4:
        st.subheader("Global Settings")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.write("**Sentiment AI**")
            msg_bot.sentiment_analysis_enabled = st.toggle("Enable Sentiment Analysis", value=True)
            st.caption("Uses local LLM to detect emotions in incoming messages.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_c2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.write("**Auto-Reply**")
            msg_bot.global_auto_reply = st.toggle("Global Auto-Reply", value=False)
            st.caption("WARNING: This will automatically send replies without confirmation.")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("Scheduled Messages Database")
        if msg_bot.scheduled_messages:
            st.dataframe(pd.DataFrame(msg_bot.scheduled_messages))
        else:
            st.caption("No pending messages.")