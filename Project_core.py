import speech_recognition as sr
import webbrowser
import pyttsx3
import musiclibrary
import requests
import google.generativeai as genai
import psutil
import config

# --- INITIALIZATION ---
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Configure Google Gemini
model = None
if config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.0-pro')

def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Audio Error: {e}")

# --- NEW: SYSTEM FUNCTIONS ---
def get_system_stats():
    """Returns CPU and RAM usage."""
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return cpu, ram, disk

def get_weather():
    """Fetches weather from OpenMeteo (Free, No Key needed)."""
    try:
        # Defaulting to New York for demo; you can change coords
        url = "https://api.open-meteo.com/v1/forecast?latitude=40.71&longitude=-74.00&current=temperature_2m,relative_humidity_2m,wind_speed_10m&temperature_unit=celsius"
        r = requests.get(url).json()
        current = r.get('current', {})
        temp = current.get('temperature_2m', 'N/A')
        humidity = current.get('relative_humidity_2m', 'N/A')
        wind = current.get('wind_speed_10m', 'N/A')
        return temp, humidity, wind
    except requests.exceptions.RequestException as e:
        print(f"Weather API Error: {e}")
        return "N/A", "N/A", "N/A"

# --- EXISTING AI FUNCTIONS ---
def listen_input():
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            text = recognizer.recognize_google(audio)
            return text.lower()
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""
    except Exception as e:
        print(f"Listening Error: {e}")
        return ""

def aiprocess(command):
    if not model:
        return "Gemini API key not configured or is invalid. Please check your config.py file."
    try:
        prompt = f"You are J.A.R.V.I.S. Keep answers short and technical. User: {command}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {e}"

def get_news():
    """Fetches top news headlines from NewsAPI."""
    if not config.NEWS_API_KEY or config.NEWS_API_KEY == "be372e0c6d404c86bd157b015b0d1d08":
        return ["News API key not configured."]
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={config.NEWS_API_KEY}"
        r = requests.get(url).json()
        if r.get("status") == "ok":
            articles = r.get("articles", [])
            headlines = [article.get("title", "") for article in articles]
            return headlines[:5]
        else:
            return ["Error fetching news."]
    except requests.exceptions.RequestException as e:
        print(f"News API Error: {e}")
        return ["Error fetching news."]

def processcommand(c):
    c = c.lower()
    response_text = ""

    if "open google" in c:
        webbrowser.open("https://google.com")
        response_text = "Opening Google."
    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")
        response_text = "Opening YouTube."
    elif c.startswith("play"):
        try:
            parts = c.split(" ", 1)
            song_name = parts[1] if len(parts) > 1 else ""
            if song_name in musiclibrary.music:
                webbrowser.open(musiclibrary.music[song_name])
                response_text = f"Playing {song_name}."
            else:
                response_text = "Song not found."
        except IndexError:
            response_text = "Please specify a song to play."
        except Exception as e:
            response_text = f"Error playing music: {e}"
    elif "system" in c or "stats" in c:
        cpu, ram, disk = get_system_stats()
        response_text = f"Systems nominal. CPU at {cpu}%. RAM at {ram}%."
    elif "weather" in c:
        temp, hum, wind = get_weather()
        response_text = f"Current temperature is {temp}°C with {hum}% humidity."
    elif "news" in c:
        headlines = get_news()
        response_text = "Here are the top headlines: \n" + "\n".join(headlines)
    else:
        response_text = aiprocess(c)

    speak(response_text)
    return response_text