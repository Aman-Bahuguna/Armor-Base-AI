import streamlit as st
import pandas as pd
import os

def render_desktop_ui(bot, listen_input_func):
    """
    Renders the Desktop Control interface.
    bot: Instance of DesktopAssistant
    listen_input_func: Function to call logic for mic input
    """
    st.markdown('<div class="armor-card"><h3 style="color:#00e0ff; margin:0;">DESKTOP AUTOMATION CONSOLE</h3></div>', unsafe_allow_html=True)

    # --- TOP ROW: VOICE & QUICK ACTIONS ---
    c_voice, c_actions = st.columns([1, 2])
    
    with c_voice:
        st.markdown('<div class="armor-card">', unsafe_allow_html=True)
        st.markdown("#### VOICE CONTROL")
        st.info("Try: 'Open Chrome', 'Set volume 50', 'Take Screenshot'")
        
        # Mic Button
        if st.button("🎙️ ACTIVATE CONTROLLER", use_container_width=True):
            with st.spinner("Processing Command..."):
                cmd = listen_input_func() # Call the passed listener function
                if cmd:
                    st.success(f"Command: {cmd}")
                    parsed = bot.parse_desktop_command(cmd)
                    if parsed:
                        st.json(parsed)
                        
                        # EXECUTE INTENT
                        intent = parsed.get('intent')
                        target = parsed.get('target')
                        val = parsed.get('value')
                        
                        msg = "Unknown Intent"
                        if intent == 'open_app':
                            ok, msg = bot.open_app(target)
                        elif intent == 'close_app':
                            ok, msg = bot.close_app(target)
                        elif intent == 'screenshot':
                            ok, msg = bot.take_screenshot()
                        elif intent == 'set_volume':
                            ok, msg = bot.set_volume(int(val))
                        elif intent == 'set_brightness':
                            ok, msg = bot.set_brightness(int(val))
                        elif intent == 'lock_screen':
                            ok, msg = bot.lock_computer()
                        
                        if ok: st.success(msg)
                        else: st.error(msg)
                    else:
                        st.error("Could not parse command.")
    
        st.markdown('</div>', unsafe_allow_html=True)

    with c_actions:
        st.markdown('<div class="armor-card">', unsafe_allow_html=True)
        st.markdown("#### QUICK ACTIONS")
        ac1, ac2, ac3, ac4 = st.columns(4)
        
        if ac1.button("📸 SCREENSHOT"):
            ok, m = bot.take_screenshot()
            st.toast(m)
            
        if ac2.button("🔒 LOCK PC"):
            bot.lock_computer()
            
        if ac3.button("🔇 MUTE"):
            bot.set_volume(0)
            
        if ac4.button("📂 EXPLORER"):
            os.startfile(".") # Opens current folder in Explorer
            
        st.write("")
        st.markdown("#### APP LAUNCHER")
        
        # Create a grid of app buttons
        apps = bot.apps
        cols = st.columns(4)
        for i, app in enumerate(apps):
            if cols[i % 4].button(f"🚀 {app['name']}", use_container_width=True):
                ok, m = bot.open_app(app['name'])
                st.toast(m)
                
        st.markdown('</div>', unsafe_allow_html=True)

    # --- MIDDLE ROW: SYSTEM SLIDERS & APP MANAGER ---
    c_sys, c_apps = st.columns([1, 1])
    
    with c_sys:
        st.markdown('<div class="armor-card">', unsafe_allow_html=True)
        st.markdown("#### SYSTEM LEVELS")
        
        vol = st.slider("VOLUME", 0, 100, 50, key="vol_slider")
        if st.button("SET VOLUME"):
            bot.set_volume(vol)
            
        bri = st.slider("BRIGHTNESS", 0, 100, 70, key="bri_slider")
        if st.button("SET BRIGHTNESS"):
            bot.set_brightness(bri)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_apps:
        st.markdown('<div class="armor-card">', unsafe_allow_html=True)
        st.markdown("#### APP MANAGER (CONFIG)")
        
        # Simple Add App Form
        with st.expander("ADD NEW APP"):
            with st.form("add_app"):
                n = st.text_input("App Name (e.g. Photoshop)")
                p = st.text_input("Path (.exe)")
                proc = st.text_input("Process Name (e.g. photoshop.exe)")
                if st.form_submit_button("SAVE MAPPING"):
                    new_app = {"name": n, "aliases": [n.lower()], "path": p, "process_name": proc}
                    bot.apps.append(new_app)
                    bot.save_config()
                    st.rerun()
                    
        # List View
        if bot.apps:
            df = pd.DataFrame(bot.apps)
            st.dataframe(df[["name", "path"]], use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- BOTTOM ROW: ACTIVITY LOGS ---
    st.markdown('<div class="armor-card">', unsafe_allow_html=True)
    st.markdown("#### ACTIVITY LOGS")
    if bot.activity_log:
        st.dataframe(pd.DataFrame(bot.activity_log), use_container_width=True)
    else:
        st.info("No recent automated actions.")
    st.markdown('</div>', unsafe_allow_html=True)