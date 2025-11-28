import speech_recognition as sr
import webbrowser
import pyttsx3
import sphinx
import pocketsphinx
import google
import musiclibrary
import requests
from openai import OpenAI
from gtts import gTTS
import pygame
import os

recognizer = sr.Recognizer()
engine = pyttsx3.init()
newsapi = "Enter your api key"

def speak(text):
    engine.say(text)
    engine.runAndWait()z``

# def speak(text):
#     tts = gTTS(text)
#     tts.save('temp.mp3')

#     pygame.mixer.init()
#     pygame.mixer.music.load()
#     pygame.mixer.music.play()

#     while pygame.mixer.music.get_busy():
#         pygame.time.Clock().tick(10)
#     os.remove('temp.mp3')
    

def aiprocess(command):
    clinet = OpenAI(api_key=" Use your own api key")
 
    completion = clinet.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
    {"role": "system", "content": "You are a virtual assistant named jarvis skilled in general tasks like Alexa and Google Cloud"},
    {"role": "user", "content": command}
    ]
    )
    return completion.choices[0].message.content


def processcommand(c):
    if "open google" in c.lower():
        webbrowser.open("https://google.com")
    elif "open github" in c.lower():
        webbrowser.open("https://github.com")
    elif "open linkedin" in c.lower():
        webbrowser.open("https://linkedin.com")
    elif "open chatgpt" in c.lower():
        webbrowser.open("https://chatgpt.com")
    elif "open youtube" in c.lower():
        webbrowser.open("https://youtube.com")
    elif c.lower().startswith("play"):
        song = c.lower.split(" ")[1]
        link = musiclibrary.music[song]
        webbrowser.open(link)

    elif "news" in c.lower():
        r = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi}")
        if r.status_code == 200:
            data = r.json()

            articles = data.get('articles',[])

            for article in articles:
                speak(article['title'])

    else:
        output = aiprocess()
        speak(output)


if __name__ ==  "__main__":
    speak("Initializing Armor........")

    while True:
        r = sr.Recognizer()
        
        print("Recognizing.....")
        try:
            with sr.Microphone() as source:
                print("Listining......")
                audio = r.listen(source, timeout=2, phrase_time_limit=2)
            word = r.recognize_google(audio)

            if (word.lower() == "armor"):
                speak("What is your next commmand sir")

                with sr.Microphone() as source:
                    print("Armor Active......")
                    audio = r.listen(source)
                    command = r.recognize_google(audio)

                    processcommand(command)

        except Exception as e:
            print("Armor error; {0}",format(e))
    



