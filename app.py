import streamlit as st
import time
import datetime
import os
import yt_dlp
import tkinter as tk
from tkinter import filedialog
from Project_core import processcommand, listen_input, get_system_stats, get_weather
# Import the new module
from email_module import EmailAssistant

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="ARMOR AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INIT EMAIL ASSISTANT ---
if 'email_bot' not in st.session_state:
    st.session_state.email_bot = EmailAssistant()

# --- CUSTOM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500&display=swap');
    
    .stApp { background-color: #050a14; font-family: 'Rajdhani', sans-serif; overflow-x: hidden; }
    header, footer {visibility: hidden;}
    [data-testid="stSidebar"] { background-color: #0b1221; border-right: 1px solid #00e0ff33; }
    
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
    
    .reactor {
        width: 150px; height: 150px;
        background: radial-gradient(circle, #00e0ff 0%, #000 70%);
        border-radius: 50%;
        box-shadow: 0 0 30px #00e0ff;
        margin: 0 auto 20px auto;
        animation: pulse 3s infinite;
    }
    
    .chat-container { height: 60vh; overflow-y: auto; display: flex; flex-direction: column-reverse; padding-right: 10px; }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #050a14; }
    ::-webkit-scrollbar-thumb { background: #00e0ff; border-radius: 3px; }

    .msg-user { text-align: right; color: #00ff99; margin: 5px 0; font-size: 1.1rem; }
    .msg-ai { text-align: left; color: #00e0ff; margin: 5px 0; border-left: 3px solid #00e0ff; padding-left: 10px; font-size: 1.1rem; }
    
    .stTextInput input, .stTextArea textarea { background-color: #0d1625; color: #00e0ff; border: 1px solid #00e0ff55; }
    .stButton button { width: 100%; background: rgba(0, 224, 255, 0.1); border: 1px solid #00e0ff; color: #00e0ff; font-family: 'Orbitron'; }
    .stButton button:hover { background: #00e0ff; color: #000; box-shadow: 0 0 20px #00e0ff; }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def open_folder_dialog():
    root = tk.Tk()
    root.withdraw() 
    root.wm_attributes('-topmost', 1) 
    folder_path = filedialog.askdirectory(master=root)
    root.destroy()
    return folder_path

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00e0ff; font-family:Orbitron;'>MENU</h2>", unsafe_allow_html=True)
    mode = st.selectbox("Select Interface", [
        "🎙️ J.A.R.V.I.S Assistant", 
        "📥 YouTube Downloader",
        "✉️ Email Protocol"
    ])
    st.divider()
    st.markdown("<div style='color:#666; font-size:12px;'>ARMOR SYSTEMS v3.1</div>", unsafe_allow_html=True)

# --- HEADER ---
curr_time = datetime.datetime.now().strftime("%H:%M")
curr_date = datetime.datetime.now().strftime("%a, %b %d")
c1, c2, c3 = st.columns([1, 4, 1])
with c1: st.markdown(f"<div style='color:#00e0ff; font-family:Orbitron;'>SYS: ONLINE</div>", unsafe_allow_html=True)
with c3: st.markdown(f"<div style='text-align:right; color:#88c0d0;'>{curr_time} | {curr_date}</div>", unsafe_allow_html=True)
st.divider()

# ==========================================
# INTERFACE 1: J.A.R.V.I.S ASSISTANT
# ==========================================
if mode == "🎙️ J.A.R.V.I.S Assistant":
    if 'history' not in st.session_state: st.session_state['history'] = []
    cpu, ram, disk = get_system_stats()
    temp, hum, wind = get_weather()

    col1, col2, col3 = st.columns([1, 1.5, 1])
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

    with col3:
        st.markdown('<div class="glass-card" style="height: 65vh;">', unsafe_allow_html=True)
        st.markdown('<h4 style="color:#00e0ff; margin-top:0;">COMMUNICATION LOG</h4>', unsafe_allow_html=True)
        chat_html = '<div class="chat-container">'
        for q, a in reversed(st.session_state['history']):
            chat_html += f'<div class="msg-user">CMD: {q}</div>'
            chat_html += f'<div class="msg-ai">>> {a}</div><hr style="border-color:#112;">'
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# INTERFACE 2: YOUTUBE DOWNLOADER
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
# INTERFACE 3: EMAIL PROTOCOL (UPDATED)
# ==========================================
elif mode == "✉️ Email Protocol":
    st.markdown("<h2 style='text-align:center; color:#00e0ff;'>SECURE COMMUNICATIONS LINK</h2>", unsafe_allow_html=True)
    
    # Init Email Draft State
    if 'email_draft' not in st.session_state:
        st.session_state['email_draft'] = {"to": "", "subject": "", "body": ""}

    tab1, tab2, tab3 = st.tabs(["COMPOSE", "INBOX", "CONTACTS"])

    # --- TAB 1: COMPOSE & VOICE ---
    with tab1:
        e_col1, e_col2 = st.columns([1, 2])
        
        with e_col1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Voice Command")
            st.info("Try: 'Send an email to John about the meeting'")
            
            if st.button("🎙️ DICTATE EMAIL"):
                with st.spinner("Listening for email instructions..."):
                    cmd = listen_input()
                    if cmd:
                        st.success(f"Recognized: {cmd}")
                        parsed = st.session_state.email_bot.parse_voice_command(cmd)
                        
                        if parsed:
                            st.session_state['email_draft']['to'] = parsed.get('recipient_email') or parsed.get('recipient_name') or ""
                            st.session_state['email_draft']['subject'] = parsed.get('subject') or ""
                            st.session_state['email_draft']['body'] = parsed.get('body') or ""
                            st.rerun()
                        else:
                            st.error("Could not understand email intent.")
                    else:
                        st.warning("No audio detected.")
            st.markdown('</div>', unsafe_allow_html=True)

        with e_col2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Secure Transmission Form")
            
            # --- INPUTS ---
            to_addr = st.text_input("RECIPIENT (Enter ANY Email Address)", value=st.session_state['email_draft']['to'], placeholder="name@example.com")
            
            # Subject and AI Generator Button
            col_sub, col_gen = st.columns([3, 1])
            with col_sub:
                subj = st.text_input("SUBJECT", value=st.session_state['email_draft']['subject'])
            with col_gen:
                st.write("") # Spacer
                st.write("") # Spacer
                if st.button("✨ AUTO-GEN", help="Generate email body from Subject"):
                    if subj:
                        with st.spinner("Generating content..."):
                            generated_body = st.session_state.email_bot.generate_email_body(subj)
                            st.session_state['email_draft']['body'] = generated_body
                            st.rerun()
                    else:
                        st.warning("Enter a subject first.")

            body = st.text_area("MESSAGE BODY", value=st.session_state['email_draft']['body'], height=200)
            
            # Sync back manual edits to state
            st.session_state['email_draft']['to'] = to_addr
            st.session_state['email_draft']['subject'] = subj
            st.session_state['email_draft']['body'] = body

            if st.button("SEND TRANSMISSION", type="primary"):
                if to_addr and body:
                    with st.spinner("Encrypting and Sending..."):
                        success, msg = st.session_state.email_bot.send_email(to_addr, subj, body)
                        if success:
                            st.success(msg)
                            st.balloons()
                            st.session_state['email_draft'] = {"to": "", "subject": "", "body": ""}
                        else:
                            st.error(msg)
                else:
                    st.warning("Recipient and Body are required.")
            st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 2: INBOX ---
    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        if st.button("🔄 FETCH RECENT EMAILS"):
            with st.spinner("Accessing Secure Server..."):
                emails = st.session_state.email_bot.fetch_recent_emails(limit=5)
                if emails:
                    for e in emails:
                        st.markdown(f"**From:** {e['sender']}")
                        st.markdown(f"**Subject:** {e['subject']}")
                        st.text(f"{e['preview']}")
                        st.divider()
                else:
                    st.info("No emails found or connection failed.")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB 3: CONTACTS ---
    with tab3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        c_col1, c_col2 = st.columns(2)
        
        with c_col1:
            st.subheader("Add Contact")
            new_name = st.text_input("Name")
            new_email = st.text_input("Email Address")
            if st.button("SAVE CONTACT"):
                if new_name and new_email:
                    res = st.session_state.email_bot.add_contact(new_name, new_email)
                    st.success(res)
                    st.rerun()
        
        with c_col2:
            st.subheader("Directory")
            contacts = st.session_state.email_bot.load_contacts()
            if contacts:
                for c in contacts:
                    st.code(f"{c['name'].capitalize()}: {c['email']}")
            else:
                st.info("No contacts in database.")
        st.markdown('</div>', unsafe_allow_html=True)