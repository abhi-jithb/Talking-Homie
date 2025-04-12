import google.generativeai as genai
import pyttsx3
import speech_recognition as sr
import json
import os

# Load config
with open("config.json") as f:
    config = json.load(f)

# Setup Gemini
genai.configure(api_key=config["api_key"])
model = genai.GenerativeModel('gemini-pro')

# Text-to-Speech setup
engine = pyttsx3.init()
engine.setProperty('rate', 160)

def speak(text):
    print(f"Homie: {text}")
    engine.say(text)
    engine.runAndWait()

# Listen from mic
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio)
        print(f"You: {query}")
        return query
    except sr.UnknownValueError:
        return "Sorry, I didn’t get that."
    except sr.RequestError:
        return "Network error"

# Memory file
MEMORY_FILE = "memory.txt"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return f.read()
    return ""

def save_memory(entry):
    with open(MEMORY_FILE, "a") as f:
        f.write(entry + "\n")

# Main chat loop
def chat():
    memory = load_memory()
    while True:
        query = listen()
        if query.lower() in ["exit", "bye", "stop"]:
            speak("Okay, see you soon!")
            break

        history = memory + "\nUser: " + query + "\nHomie:"
        response = model.generate_content(history)
        answer = response.text.strip()

        speak(answer)
        save_memory(f"User: {query}\nHomie: {answer}")

if __name__ == "__main__":
    speak(f"Hello {config['user']}, I'm {config['name']}, your AI homie!")
    chat()
