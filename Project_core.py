import speech_recognition as sr
import webbrowser
import pyttsx3
import musiclibrary
import requests
import google.generativeai as genai
import psutil
import config
import ollama

# --- IMPORT MODULES ---
try:
    from email_module import EmailAssistant
    email_bot = EmailAssistant()
except ImportError:
    email_bot = None

try:
    from messaging_module import MessagingAssistant
    msg_bot = MessagingAssistant()
except ImportError:
    msg_bot = None

try:
    from reminders_module import RemindersAssistant
    remind_bot = RemindersAssistant()
except ImportError:
    remind_bot = None

# --- INITIALIZATION ---
recognizer = sr.Recognizer()
try:
    engine = pyttsx3.init()
except:
    engine = None

model = None
if hasattr(config, 'GEMINI_API_KEY') and config.GEMINI_API_KEY:
    try:
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except: pass

def speak(text):
    if not engine: return
    try:
        engine.say(text)
        engine.runAndWait()
    except: pass

# --- CORE FUNCTIONS ---
def get_system_stats():
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return cpu, ram, disk

def get_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=40.71&longitude=-74.00&current=temperature_2m,relative_humidity_2m,wind_speed_10m&temperature_unit=celsius"
        r = requests.get(url, timeout=5).json()
        c = r.get('current', {})
        return c.get('temperature_2m', 'N/A'), c.get('relative_humidity_2m', 'N/A'), c.get('wind_speed_10m', 'N/A')
    except: return "N/A", "N/A", "N/A"

def listen_input():
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=10)
            return recognizer.recognize_google(audio).lower()
    except: return ""

def aiprocess(command):
    try:
        response = ollama.chat(
            model='llama3.2',
            messages=[{'role': 'system', 'content': 'You are J.A.R.V.I.S. Keep answers short, technical.'}, {'role': 'user', 'content': command}]
        )
        return response['message']['content']
    except Exception as e:
        return f"AI Error: {e}"

def get_news():
    if not hasattr(config, 'NEWS_API_KEY'): return ["Config Missing"]
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={config.NEWS_API_KEY}"
        r = requests.get(url, timeout=5).json()
        return [a['title'] for a in r.get('articles', [])][:5] if r.get('status')=='ok' else ["News Error"]
    except: return ["News Error"]

def processcommand(c):
    c = c.lower()
    resp = ""

    if c.startswith("open "):
        site = c.replace("open ", "").replace(" website", "").strip()
        webbrowser.open(f"https://duckduckgo.com/?q=!ducky+{site}")
        resp = f"Opening {site}."
    elif c.startswith("play"):
        try:
            song = c.split(" ", 1)[1]
            if song in musiclibrary.music:
                webbrowser.open(musiclibrary.music[song])
                resp = f"Playing {song}."
            else: resp = "Song not found."
        except: resp = "Error."
    elif "system" in c:
        cpu, ram, _ = get_system_stats()
        resp = f"CPU: {cpu}%, RAM: {ram}%."
    elif "weather" in c:
        t, h, _ = get_weather()
        resp = f"{t}°C, {h}% Humidity."
    elif "email" in c: resp = "Use Email Protocol."
    elif "message" in c: resp = "Use Messaging Assistant."
    elif "remind" in c or "list" in c: resp = "Use Smart Reminders Tab."
    else: resp = aiprocess(c)

    speak(resp)
    return resp