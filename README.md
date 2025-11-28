# 🤖 Armor – Voice Controlled AI Assistant (Python)

Armor is a voice-activated AI assistant built with Python that can perform various tasks such as opening websites, reading news, and processing AI-powered responses using OpenAI’s API. It functions similarly to virtual assistants like Alexa or Google Assistant.

---

## 🧠 Features

- 🎤 Voice activation using the keyword **"Armor"**
- 🔗 Opens websites like Google, YouTube, GitHub, LinkedIn, ChatGPT
- 📰 Fetches and reads top news headlines (via NewsAPI)
- 🎵 Plays music using predefined song links (`musiclibrary`)
- 💬 Processes complex user commands using **OpenAI's GPT model**
- 🗣️ Responds with speech (using `pyttsx3` or Google Text-to-Speech)

---

## 🚀 Technologies Used

- `speech_recognition` – for capturing voice input
- `webbrowser` – to open websites
- `pyttsx3` or `gTTS + pygame` – for text-to-speech
- `openai` – for AI-powered responses
- `requests` – for accessing NewsAPI
- `pocketsphinx` (optional) – for offline voice recognition
- `pygame` – for playing audio (if using gTTS)
- `musiclibrary` – for song link mapping *(custom module)*

---

## 📦 Requirements

Install required packages using pip:

```bash
pip install speechrecognition pyttsx3 openai requests pygame gtts
pip install pocketsphinx
