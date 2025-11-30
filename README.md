# 🤖 Armor – Voice Controlled AI Assistant (Python)

Armor is a voice-activated AI assistant built with Python that can perform various tasks such as opening websites, reading news, and processing AI-powered responses using Google's Gemini API. It functions similarly to virtual assistants like Alexa or Google Assistant.

---

## 🧠 Features

- 🎤 Voice activation using the keyword **"Armor"**
- 🔗 Opens websites like Google, YouTube, GitHub, LinkedIn, ChatGPT
- 📰 Fetches and reads top news headlines (via NewsAPI)
- 🎵 Plays music using predefined song links (`musiclibrary`)
- 💬 Processes complex user commands using **Google's Gemini model**
- 🗣️ Responds with speech (using `pyttsx3`)
- 🌐 A web-based UI built with Streamlit

---

## 🚀 Technologies Used

- `speech_recognition` – for capturing voice input
- `webbrowser` – to open websites
- `pyttsx3` – for text-to-speech
- `google-generativeai` – for AI-powered responses
- `requests` – for accessing NewsAPI
- `pocketsphinx` (optional) – for offline voice recognition
- `musiclibrary` – for song link mapping *(custom module)*
- `streamlit` – for the web interface
- `psutil` – for system stats

---

## 📦 Requirements

1.  **Install required packages using pip:**

    ```bash
    pip install speechrecognition pyttsx3 google-generativeai requests pocketsphinx psutil streamlit
    ```

2.  **Set up your API keys:**

    *   Create a file named `config.py` in the root directory of the project.
    *   Add the following content to `config.py`:

        ```python
        # API Keys
        NEWS_API_KEY = "YOUR_NEWS_API_KEY"
        GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
        ```

    *   Replace `"YOUR_NEWS_API_KEY"` with your NewsAPI key.
    *   Replace `"YOUR_GEMINI_API_KEY"` with your Google Gemini API key.

3.  **Run the application:**

    ```bash
    streamlit run app.py
    ```

