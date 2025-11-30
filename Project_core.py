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

# --- IMPORT NEW MODULE ---
try:
    from email_module import EmailAssistant
    email_bot = EmailAssistant()
except ImportError:
    print("Email module not found or config missing.")
    email_bot = None

# --- INITIALIZATION ---
# Initialize recognizer
recognizer = sr.Recognizer()

# Initialize Engine (Safe Initialization)
try:
    engine = pyttsx3.init()
except Exception as e:
    print(f"TTS Init Error: {e}")
    engine = None

# Configure Google Gemini (Existing)
model = None
if hasattr(config, 'GEMINI_API_KEY') and config.GEMINI_API_KEY:
    try:
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
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
        url = "https://api.open-meteo.com/v1/forecast?latitude=40.71&longitude=-74.00&current=temperature_2m,relative_humidity_2m,wind_speed_10m&temperature_unit=celsius"
        r = requests.get(url, timeout=5).json()
        current = r.get('current', {})
        return current.get('temperature_2m', 'N/A'), current.get('relative_humidity_2m', 'N/A'), current.get('wind_speed_10m', 'N/A')
    except Exception as e:
        print(f"Weather API Error: {e}")
        return "N/A", "N/A", "N/A"

# --- AI & INPUT FUNCTIONS ---
def listen_input():
    """Listens to the microphone and returns text."""
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            # Increased timeout slightly for email dictation
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=15)
            text = recognizer.recognize_google(audio)
            return text.lower()
    except sr.WaitTimeoutError:
        return "" 
    except sr.UnknownValueError:
        return ""
    except Exception as e:
        print(f"Listening Error: {e}")
        return ""

def aiprocess(command):
    try:
        response = ollama.chat(
            model='llama3.2',
            messages=[
                {'role': 'system', 'content': 'You are J.A.R.V.I.S. Keep answers short, technical, and precise.'},
                {'role': 'user', 'content': command}
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
            return [article.get("title", "") for article in r.get("articles", [])][:5]
        return ["Could not fetch news."]
    except Exception as e:
        return [f"Error fetching news: {e}"]

def processcommand(c):
    c = c.lower()
    response_text = ""

    if c.startswith("open "):
        site_name = c.replace("open ", "").replace(" website", "").strip()
        if site_name:
            url = f"https://duckduckgo.com/?q=!ducky+{site_name}"
            webbrowser.open(url)
            response_text = f"Opening {site_name}."
        else:
            response_text = "Which website should I open?"

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

    # --- EMAIL ROUTING TIP ---
    elif "email" in c or "send mail" in c:
        response_text = "Please switch to the Email Protocol interface to manage communications securely."

    else:
        response_text = aiprocess(c)

    speak(response_text)
    return response_text