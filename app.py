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
from email_module import EmailAssistant
from messaging_module import MessagingAssistant
from reminders_module import RemindersAssistant
from desktop_module import DesktopAssistant

# --- IMPORT UI MODULES ---
import ui_desktop  # New separate UI file for Desktop Control

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

# 2. Global Bots (Cached Resources)
@st.cache_resource
def get_bots():
    return MessagingAssistant(), RemindersAssistant(), DesktopAssistant()

msg_bot, rem_bot, desk_bot = get_bots()

# --- CUSTOM CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;400;600&display=swap');

    /* Global App Styling */
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

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(5, 10, 20, 0.95);
        border-right: 1px solid rgba(0, 224, 255, 0.2);
    }
    
    /* Glassmorphism Cards */
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

    /* Reactor Animation */
    .reactor {
        width: 140px; height: 140px;
        background: radial-gradient(circle, #00e0ff 0%, transparent 70%);
        border-radius: 50%;
        border: 4px solid rgba(0, 224, 255, 0.3);
        box-shadow: 0 0 30px #00e0ff, inset 0 0 30px #00e0ff;
        animation: pulse 3s infinite ease-in-out;
        margin: 0 auto;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 20px #00e0ff; opacity: 0.7; }
        50% { transform: scale(1.05); box-shadow: 0 0 60px #00e0ff; opacity: 1; }
        100% { transform: scale(0.95); box-shadow: 0 0 20px #00e0ff; opacity: 0.7; }
    }

    /* Inputs & Buttons */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(10, 20, 30, 0.8);
        border: 1px solid rgba(0, 224, 255, 0.3);
        color: #fff;
        font-family: 'Rajdhani', sans-serif;
    }
    .stButton > button {
        background: rgba(0, 224, 255, 0.05);
        border: 1px solid #00e0ff;
        color: #00e0ff;
        font-family: 'Orbitron', sans-serif;
    }
    .stButton > button:hover {
        background: rgba(0, 224, 255, 0.2);
        box-shadow: 0 0 15px #00e0ff;
        color: #fff;
    }

    /* Utility Classes */
    .stat-label { font-size: 0.9rem; color: #88c0d0; text-transform: uppercase; }
    .stat-val { font-size: 1.5rem; font-weight: bold; font-family: 'Orbitron'; color: #fff; }
    
    /* Progress Bar Hack */
    .stProgress > div > div > div > div {
        background-color: #00e0ff;
        box-shadow: 0 0 10px #00e0ff;
    }
    
    /* Chat Bubbles */
    .chat-container { height: 60vh; overflow-y: auto; display: flex; flex-direction: column-reverse; padding: 10px; }
    .bubble { padding: 10px 15px; border-radius: 10px; margin-bottom: 10px; max-width: 80%; }
    .bubble-user { background: rgba(0, 255, 136, 0.1); border-right: 3px solid #00ff88; align-self: flex-end; text-align: right; }
    .bubble-ai { background: rgba(0, 224, 255, 0.1); border-left: 3px solid #00e0ff; align-self: flex-start; text-align: left; }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def open_folder_dialog():
    root = tk.Tk(); root.withdraw(); root.wm_attributes('-topmost', 1)
    path = filedialog.askdirectory(master=root); root.destroy()
    return path

def render_stat_card(label, value, color="#00e0ff"):
    return f"""
    <div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:8px; border-left: 3px solid {color}; flex:1; margin:0 5px;">
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
        [
            "🎙️ COMMAND CENTER", 
            "🖥️ DESKTOP CONTROL",
            "⏰ SMART REMINDERS",
            "📥 DOWNLOADER", 
            "✉️ EMAIL PROTOCOL", 
            "💬 MESSAGING"
        ],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Active Reminders Counter
    pending_count = len([r for r in rem_bot.reminders if r['status'] == 'pending'])
    st.metric("PENDING TASKS", pending_count)
    
    st.divider()
    
    # System Stats
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
    
    c1, c2 = st.columns([1, 1.5])
    with c1:
        # Reactor Visual
        st.markdown('<div class="armor-card"><div class="reactor"></div></div>', unsafe_allow_html=True)
        
        # Status Cards
        temp, hum, wind = get_weather()
        st.markdown(f"""
        <div class="armor-card">
            <div style="display:flex; justify-content:space-between;">
                {render_stat_card("TEMP", f"{temp}°C", "#ffcc00")}
                {render_stat_card("HUMIDITY", f"{hum}%", "#00ff88")}
                {render_stat_card("WIND", f"{wind}km", "#00e0ff")}
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
        
        chat_html = '<div class="chat-container">'
        for q, a in reversed(st.session_state['history']):
            chat_html += f'<div class="bubble bubble-user">{q}</div>'
            chat_html += f'<div class="bubble bubble-ai">{a}</div>'
        chat_html += '</div>'
        
        st.markdown(chat_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# MODULE 2: DESKTOP CONTROL (NEW)
# ==========================================
elif mode == "🖥️ DESKTOP CONTROL":
    # Delegate rendering to the separate UI file
    ui_desktop.render_desktop_ui(desk_bot, listen_input)

# ==========================================
# MODULE 3: SMART REMINDERS
# ==========================================
elif mode == "⏰ SMART REMINDERS":
    with st.container():
        st.markdown('<div class="armor-card">', unsafe_allow_html=True)
        c_voice, c_text = st.columns([1, 3])
        
        with c_voice:
            st.markdown("#### VOICE ENTRY")
            if st.button("🎙️ ADD TASK", use_container_width=True):
                with st.spinner("Listening..."):
                    cmd = listen_input()
                    if cmd:
                        parsed = rem_bot.parse_command(cmd)
                        if parsed:
                            if parsed['intent'] == 'reminder':
                                msg = rem_bot.add_reminder(parsed['content'], parsed['time'], parsed.get('category', 'General'))
                                st.success(msg)
                            elif parsed['intent'] == 'todo':
                                msg = rem_bot.add_todo(parsed['content'])
                                st.success(msg)
                            elif parsed['intent'] == 'shopping':
                                msg = rem_bot.add_shopping(parsed['content'])
                                st.success(msg)
                            else:
                                st.error("Unknown intent.")
                        else: st.error("Could not understand command.")
        
        with c_text:
            st.markdown("#### MANUAL ENTRY")
            with st.form("quick_add"):
                c_t1, c_t2, c_t3 = st.columns([2, 1, 1])
                desc = c_t1.text_input("Description", placeholder="Buy milk / Meeting at 5pm")
                cat = c_t2.selectbox("Type", ["Reminder", "To-Do", "Shopping"])
                sub = c_t3.form_submit_button("ADD ITEM", use_container_width=True)
                if sub and desc:
                    if cat == "Reminder":
                        rem_bot.add_reminder(desc, "today") 
                        st.success("Reminder added (Default time: Today/Now)")
                    elif cat == "To-Do":
                        rem_bot.add_todo(desc)
                        st.success("Added to To-Do")
                    else:
                        rem_bot.add_shopping(desc)
                        st.success("Added to Shopping List")
        st.markdown('</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["⏳ REMINDERS", "📋 TO-DO LIST", "🛒 SHOPPING"])
    
    with tab1:
        sorted_rems = sorted(rem_bot.reminders, key=lambda x: (x['status'] != 'triggered', x['time']))
        if not sorted_rems: st.info("No active reminders.")
        
        for r in sorted_rems:
            # Inline CSS for reminder items
            st_class = "border-left: 4px solid #ff3333; background: rgba(255, 50, 50, 0.1);" if r['status'] == 'triggered' else "border-bottom: 1px solid #333;"
            status_icon = "🔴 DUE" if r['status'] == 'triggered' else "🟢"
            
            with st.container():
                st.markdown(f"""
                <div style="padding: 10px; {st_class} display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                    <div>
                        <strong style="font-size:1.1em; color:#fff">{r['title']}</strong><br>
                        <small style="color:#00e0ff">{r['time']}</small>
                    </div>
                    <div style="font-weight:bold;">{status_icon}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("DISMISS", key=f"del_rem_{r['id']}"):
                    rem_bot.delete_item("reminder", r['id'])
                    st.rerun()

    with tab2:
        if not rem_bot.todo_list: st.info("To-Do list is empty.")
        for t in rem_bot.todo_list:
            c_check, c_txt, c_del = st.columns([0.5, 4, 1])
            is_done = t['status'] == 'completed'
            if c_check.checkbox("", value=is_done, key=f"chk_todo_{t['id']}"):
                rem_bot.toggle_status("todo", t['id'])
                st.rerun()
            st_style = "text-decoration:line-through; color:#666;" if is_done else "color:#fff;"
            c_txt.markdown(f"<span style='{st_style} font-size:1.1em;'>{t['item']}</span>", unsafe_allow_html=True)
            if c_del.button("❌", key=f"del_todo_{t['id']}"):
                rem_bot.delete_item("todo", t['id'])
                st.rerun()

    with tab3:
        if not rem_bot.shopping_list: st.info("Shopping list is empty.")
        for s in rem_bot.shopping_list:
            c_check, c_txt, c_del = st.columns([0.5, 4, 1])
            is_done = s['status'] == 'completed'
            if c_check.checkbox("", value=is_done, key=f"chk_shop_{s['id']}"):
                rem_bot.toggle_status("shopping", s['id'])
                st.rerun()
            st_style = "text-decoration:line-through; color:#666;" if is_done else "color:#fff;"
            c_txt.markdown(f"<span style='{st_style} font-size:1.1em;'>{s['item']} (Qty: {s['quantity']})</span>", unsafe_allow_html=True)
            if c_del.button("❌", key=f"del_shop_{s['id']}"):
                rem_bot.delete_item("shopping", s['id'])
                st.rerun()

# ==========================================
# MODULE 4: DOWNLOADER
# ==========================================
elif mode == "📥 DOWNLOADER":
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
# MODULE 5: EMAIL PROTOCOL
# ==========================================
elif mode == "✉️ EMAIL PROTOCOL":
    if 'email_draft' not in st.session_state:
        st.session_state['email_draft'] = {"to": "", "subject": "", "body": ""}

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
# MODULE 6: MESSAGING
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