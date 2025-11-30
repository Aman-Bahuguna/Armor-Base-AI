import speech_recognition as sr
import webbrowser
import pyttsx3
import musiclibrary
import requests
import google.generativeai as genai
import psutil
import config
from groq import Groq
import ollama

# --- INITIALIZATION ---
# Initialize recognizer
recognizer = sr.Recognizer()

# Initialize Engine (Safe Initialization)
try:
    engine = pyttsx3.init()
    # Optional: Set voice properties here if needed
except Exception as e:
    print(f"TTS Init Error: {e}")
    engine = None

# Configure Google Gemini
model = None
if hasattr(config, 'GEMINI_API_KEY') and config.GEMINI_API_KEY:
    try:
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash') # Updated to a faster, newer model
    except Exception as e:
        print(f"Gemini Config Error: {e}")

def speak(text):
    """Speaks text using system TTS."""
    if not engine:
        return
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Audio Error: {e}")

# --- SYSTEM FUNCTIONS ---
def get_system_stats():
    """Returns CPU and RAM usage."""
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return cpu, ram, disk

def get_weather():
    """Fetches weather from OpenMeteo."""
    try:
        # Defaulting to New York for demo
        url = "https://api.open-meteo.com/v1/forecast?latitude=40.71&longitude=-74.00&current=temperature_2m,relative_humidity_2m,wind_speed_10m&temperature_unit=celsius"
        r = requests.get(url, timeout=5).json()
        current = r.get('current', {})
        temp = current.get('temperature_2m', 'N/A')
        humidity = current.get('relative_humidity_2m', 'N/A')
        wind = current.get('wind_speed_10m', 'N/A')
        return temp, humidity, wind
    except Exception as e:
        print(f"Weather API Error: {e}")
        return "N/A", "N/A", "N/A"

# --- AI & INPUT FUNCTIONS ---
def listen_input():
    """Listens to the microphone and returns text."""
    try:
        with sr.Microphone() as source:
            # Adjust for ambient noise briefly to avoid long waits
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            # Listen with a timeout so it doesn't hang forever
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            text = recognizer.recognize_google(audio)
            return text.lower()
    except sr.WaitTimeoutError:
        return "" # No speech detected
    except sr.UnknownValueError:
        return "" # Speech unintelligible
    except Exception as e:
        print(f"Listening Error: {e}")
        return ""

def aiprocess(command):
    try:
        # This talks to the Ollama app running on your PC
        response = ollama.chat(
            model='llama3.2',
            messages=[
                {
                    'role': 'system',
                    'content': 'You are J.A.R.V.I.S. Keep answers short, technical, and precise.'
                },
                {
                    'role': 'user',
                    'content': command
                }
            ]
        )
        return response['message']['content']
    except Exception as e:
        return f"Local AI Error: {e}. Is Ollama running?"
    
    
def get_news():
    if not hasattr(config, 'NEWS_API_KEY') or not config.NEWS_API_KEY:
        return ["News API key missing."]
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={config.NEWS_API_KEY}"
        r = requests.get(url, timeout=5).json()
        if r.get("status") == "ok":
            articles = r.get("articles", [])
            headlines = [article.get("title", "") for article in articles]
            return headlines[:5]
        return ["Could not fetch news."]
    except Exception as e:
        return [f"Error fetching news: {e}"]

def processcommand(c):
    c = c.lower()
    response_text = ""

    # --- NEW: UNIVERSAL WEBSITE OPENER ---
    # Triggered by "open [name]" or "open [name] website"
    if c.startswith("open "):
        # 1. Clean the command to get just the website name
        #    e.g., "open dribbble website" -> "dribbble"
        site_name = c.replace("open ", "").replace(" website", "").strip()
        
        if site_name:
            # 2. Use DuckDuckGo's !ducky feature for instant redirect
            #    This finds the best matching site and opens it immediately.
            url = f"https://duckduckgo.com/?q=!ducky+{site_name}"
            
            # 3. Open in the System Default Browser
            webbrowser.open(url)
            response_text = f"Opening {site_name}."
        else:
            response_text = "Which website should I open?"

    # --- EXISTING COMMANDS ---
    elif c.startswith("play"):
        try:
            parts = c.split(" ", 1)
            song_name = parts[1] if len(parts) > 1 else ""
            if song_name in musiclibrary.music:
                webbrowser.open(musiclibrary.music[song_name])
                response_text = f"Playing {song_name}."
            else:
                response_text = "Song not found in library."
        except Exception:
            response_text = "Please specify a song."

    elif "system" in c or "stats" in c:
        cpu, ram, disk = get_system_stats()
        response_text = f"System Status: CPU at {cpu}%. RAM at {ram}%."

    elif "weather" in c:
        temp, hum, wind = get_weather()
        response_text = f"It is currently {temp} degrees with {hum} percent humidity."

    elif "news" in c:
        headlines = get_news()
        response_text = "Top Headlines: " + ". ".join(headlines)

    else:
        # Default to AI for conversation
        response_text = aiprocess(c)

    speak(response_text)
    return response_text