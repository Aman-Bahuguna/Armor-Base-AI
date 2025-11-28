# app.py

import streamlit as st
from Project_core import processcommand # Import the core logic

# --- UI Setup ---
# The image style suggests a dark theme and custom CSS is recommended
# to achieve the "JERVIS" look (e.g., glowing text, wave visualizer).
# Streamlit allows for basic custom CSS to override defaults.

# Set the page configuration for a darker look
st.set_page_config(
    page_title="ARMOR AI Assistant",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom CSS for a dark, futuristic look (Partial example, full styling is complex)
st.markdown("""
<style>
    /* Global Background and Text */
    .stApp {
        background-color: #000408; /* Very dark blue/black */
        color: #00FFFF; /* Cyan for text */
    }
    /* Header/Title */
    h1 {
        text-align: center;
        color: #00FFFF;
        text-shadow: 0 0 10px #00FFFF, 0 0 20px #00FFFF; /* Glowing effect */
    }
    /* Input/Output Boxes (Attempting CMD box style) */
    .stTextInput>div>div>input {
        color: #00FF00; /* Green for input text */
        background-color: #0a0e14;
        border: 1px solid #00FFFF;
    }
    /* Command Output Box Styling (for a terminal-like feel) */
    .cmd-box {
        background-color: #0a0e14;
        border: 1px solid #00FFFF;
        padding: 10px;
        height: 200px; /* Fixed height for the output window */
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# --- Title Section ---
st.title("ARMOR") # Corresponds to the JERVIS title
st.write("---")

# --- Voice Wave Visualizer Placeholder  ---
# Streamlit does not have a built-in dynamic wave visualizer,
# so we'll use a static placeholder and text.

# Placeholder for the dynamic sound wave (as seen in the image)
# For a real implementation, this would require complex frontend code (JS/React) or a custom Streamlit component.
st.markdown("<div style='text-align:center; margin: 20px 0;'><h1><span style='color: #00FFFF; font-size: 40px;'>🔊</span></h1></div>", unsafe_allow_html=True)


# --- Output (CMD) Box ---
# This mimics the "CMD" box in the bottom right
st.header("CMD")
if 'command_history' not in st.session_state:
    st.session_state['command_history'] = ["System initialized. Awaiting input...", ""]

# Display the command history
history_display = "\n".join(st.session_state['command_history'])
st.markdown(f"<div class='cmd-box'>{history_display}</div>", unsafe_allow_html=True)

# --- Input Section ---
def handle_input():
    user_input = st.session_state.text_input
    if user_input:
        # 1. Process the command
        output_text = processcommand(user_input) # Call your modified logic

        # 2. Update the history for display
        st.session_state['command_history'].append(f"User: {user_input}")
        st.session_state['command_history'].append(f"Armor: {output_text}")
        
        # 3. Clear the input box (Important for Streamlit)
        st.session_state.text_input = "" 

st.header("INPUT")
st.text_input("Enter your command here:", key="text_input", on_change=handle_input, label_visibility="collapsed")


# --- Top Menu Placeholder (SETTING, EDIT THEME, HELP) ---
# For a basic Streamlit app, this is often placed in the sidebar or an expander.
# To keep the image look, we'll use simple markdown placeholders.
st.markdown("""
<div style='display: flex; justify-content: space-around; padding: 10px; border-bottom: 1px solid #00FFFF;'>
    <span style='color: #00FFFF; cursor: pointer;'>SETTING</span>
    <span style='color: #00FFFF; cursor: pointer;'>EDIT THEME</span>
    <span style='color: #00FFFF; cursor: pointer;'>HELP</span>
</div>
""", unsafe_allow_html=True)

# You would run this with: `streamlit run app.py`