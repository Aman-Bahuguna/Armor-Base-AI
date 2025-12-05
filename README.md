# 🛡️ ARMOR AI - Advanced Modular Voice Assistant

**Armor AI** is a comprehensive, voice-activated virtual assistant built with Python and Streamlit. Designed with a modular architecture, it functions as a central command hub for desktop automation, security surveillance, communication (Email/WhatsApp/Telegram), and task management. It leverages **Google Gemini** for general intelligence and **Ollama (Llama 3.2)** for local intent parsing.

---

## 🚀 Features

### 🎙️ Command Center (J.A.R.V.I.S Mode)
* **Voice & Text Input:** Interact via microphone or manual text input.
* **AI Intelligence:** Powered by **Google Gemini 1.5 Flash** for general queries and **Ollama (Llama 3.2)** for local command parsing.
* **System Diagnostics:** Real-time monitoring of CPU, RAM, and Disk usage.
* **Weather & News:** Live updates via Open-Meteo and NewsAPI.

### 🛡️ Security System
* **Surveillance Mode:** Active webcam monitoring with motion detection using OpenCV.
* **Intruder Alerts:** Automatically logs motion events with timestamps and snapshots.
* **Remote Notifications:** Sends alerts via Email and Telegram when motion is detected.

### 🖥️ Desktop Automation
* **App Control:** Voice commands to open/close specific applications (configured via `apps_config.json`).
* **System Control:** Adjust volume, brightness, take screenshots, or lock the workstation.
* **UI Dashboard:** A dedicated "App Launcher" grid within the interface.

### ✉️ & 💬 Communication Protocol
* **Email Assistant:** Compose and send emails using voice dictation. Includes an "Auto-Gen" feature to write email bodies using AI based on a subject line.
* **Messaging Hub:** Send WhatsApp messages (via desktop automation) and Telegram messages (via Bot API).
* **Sentiment Analysis:** Analyzes incoming Telegram messages for sentiment and suggests AI-generated replies.

### 🛠️ Utilities
* **Smart Reminders:** Manage Reminders, To-Do lists, and Shopping lists with recurring task support.
* **Media Downloader:** Built-in tool using `yt_dlp` to download video or audio from YouTube.

---

## 📦 Installation & Setup

### 1. Prerequisites
* Python 3.10+
* **Ollama:** You must have [Ollama](https://ollama.com/) installed and the `llama3.2` model pulled (`ollama pull llama3.2`) as it is used for local intent parsing.
* **FFmpeg:** Required for the media downloader functionality.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
