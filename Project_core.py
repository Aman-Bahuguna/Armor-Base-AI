import speech_recognition as sr
import webbrowser
import pyttsx3
import musiclibrary
import requests
import google.generativeai as genai
import os

# --- INITIALIZATION ---
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# !!! ENTER YOUR KEYS HERE !!!
# Get this from: https://newsapi.org/
newsapi = "be372e0c6d404c86bd157b015b0d1d08"

# Get this from: https://aistudio.google.com/app/apikey
gemini_api_key = "AIzaSyDO7dTU8tBbYpM_9T7WnlwQvlppdWSgFAQ"

# Configure Google Gemini
if gemini_api_key != "AIzaSyDO7dTU8tBbYpM_9T7WnlwQvlppdWSgFAQ":
    genai.configure(api_key=gemini_api_key)
    # Use the flash model for speed, or 'gemini-pro' for better reasoning
    model = genai.GenerativeModel('gemini-1.5-flash')

def speak(text):
    """Speaks the text using the system's text-to-speech engine."""
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Audio Error: {e}")

def aiprocess(command):
    """Sends the command to Google Gemini and gets a response."""
    if gemini_api_key == "AIzaSyDO7dTU8tBbYpM_9T7WnlwQvlppdWSgFAQ":
        return "Please set your Gemini API key in Project_core.py"
    
    try:
        # Prompt engineering to make it act like Armor
        prompt = f"You are Armor, a helpful and cool virtual assistant. Keep your answer short and concise. User asks: {command}"
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Connection Error: {e}"

def processcommand(c):
    """Process the command and return a text response for the UI."""
    response_text = ""
    c = c.lower()

    if "open google" in c:
        webbrowser.open("https://google.com")
        response_text = "Accessing Google Database..."
        
    elif "open github" in c:
        webbrowser.open("https://github.com")
        response_text = "Opening GitHub Repositories..."

    elif "open linkedin" in c:
        webbrowser.open("https://linkedin.com")
        response_text = "Connecting to LinkedIn..."

    elif "open chatgpt" in c:
        webbrowser.open("https://chatgpt.com")
        response_text = "Launching ChatGPT Interface..."

    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")
        response_text = "Opening YouTube..."

    elif c.startswith("play"):
        try:
            # Splits "play songname" to get "songname"
            # Fixed: Check if there is actually a song name
            parts = c.split(" ", 1)
            if len(parts) > 1:
                song = parts[1]
                if song in musiclibrary.music:
                    link = musiclibrary.music[song]
                    webbrowser.open(link)
                    response_text = f"Playing {song} from library."
                else:
                    response_text = f"Song '{song}' not found in library."
            else:
                response_text = "Please specify a song name."
        except Exception:
            response_text = "Error processing play command."

    elif "news" in c:
        if newsapi == "YOUR_NEWS_API_KEY":
            response_text = "Please set your NewsAPI key."
        else:
            try:
                r = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi}")
                if r.status_code == 200:
                    data = r.json()
                    articles = data.get('articles', [])
                    headlines = [a['title'] for a in articles[:3]]
                    response_text = "Latest Headlines: " + " | ".join(headlines)
                else:
                    response_text = "Failed to retrieve news feed."
            except Exception as e:
                response_text = f"Network Error: {e}"

    else:
        # Send everything else to the AI (Gemini)
        response_text = aiprocess(c)

    # Speak the result
    speak(response_text)
    return response_text