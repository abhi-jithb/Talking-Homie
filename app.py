import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import webbrowser
import requests
import pywhatkit
import re
import random
import os
import subprocess
import datetime
import json
import pyjokes
import pyautogui
import psutil
import ctypes
import winsound
import time
from plyer import notification
from collections import deque
import threading
import queue
from datetime import datetime, timedelta

# STEP 1: Configure Gemini
genai.configure(api_key="AIzaSyDjqdMjWoswrR3LTOezdGOzSGc78cMorMw")
model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

# STEP 2: Initialize voice engine
engine = pyttsx3.init()
# Get available voices
voices = engine.getProperty('voices')
# Set a voice to a more sweet or cool one (based on your system's voices)
# You may need to adjust this depending on what voices are available on your system
engine.setProperty('voice', voices[0].id)  # Use a different voice (index may vary)

# Optionally, adjust speech rate and pitch for a cooler sound
engine.setProperty('rate', 190)  # Speed of speech (lower = slower)
engine.setProperty('pitch', 150)  # Pitch of voice

# Add after other global variables
conversation_history = deque(maxlen=10)  # Store last 10 interactions
user_context = {}  # Store user preferences and context

class ReminderManager:
    def __init__(self):
        self.reminder_queue = queue.Queue()
        self.reminder_thread = threading.Thread(target=self._process_reminders, daemon=True)
        self.reminder_thread.start()
        self.engine = pyttsx3.init()

    def add_reminder(self, text, seconds):
        try:
            # Calculate the reminder time
            reminder_time = datetime.now() + timedelta(seconds=seconds)
            
            # Add to queue
            self.reminder_queue.put({
                'text': text,
                'time': reminder_time
            })
            
            # Show initial notification
            notification.notify(
                title="Reminder Set",
                message=f"Will remind you about: {text} in {seconds} seconds",
                timeout=5
            )
            
            return True
        except Exception as e:
            print(f"Error adding reminder: {e}")
            return False

    def _process_reminders(self):
        while True:
            try:
                # Get the next reminder
                reminder = self.reminder_queue.get()
                current_time = datetime.now()
                
                # Calculate time to wait
                wait_time = (reminder['time'] - current_time).total_seconds()
                if wait_time > 0:
                    time.sleep(wait_time)
                
                # Time's up - notify
                notification.notify(
                    title="Reminder!",
                    message=f"Time's up! {reminder['text']}",
                    timeout=10
                )
                
                # Play sound
                winsound.Beep(1000, 1000)
                
                # Speak the reminder
                try:
                    self.engine.say(f"Reminder: {reminder['text']}")
                    self.engine.runAndWait()
                except Exception as e:
                    print(f"Error speaking reminder: {e}")
                    print(f"Reminder: {reminder['text']}")
                
            except Exception as e:
                print(f"Error in reminder processing: {e}")
                time.sleep(1)  # Prevent tight loop on error

# Initialize reminder manager
reminder_manager = ReminderManager()

def speak(text, is_detailed=False):
    try:
        if not is_detailed:
            minimal = text.strip().split(".")[0]
    print(f"Jarvis: {minimal}")
    engine.say(minimal)
        else:
            print(f"Jarvis: {text}")
            engine.say(text)
    engine.runAndWait()
    except RuntimeError as e:
        # If run loop already started, just print the message
        print(f"Jarvis: {text}")
    except Exception as e:
        print(f"Error in speak: {e}")
        print(f"Jarvis: {text}")


def strip_markdown(text):
    # Remove **bold**, *italic*, `code`, etc.
    clean_text = re.sub(r'(\*{1,2}|`)', '', text)
    return clean_text


def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=1)
        r.pause_threshold = 0.8
        r.energy_threshold = 4000  # Adjust this value based on your microphone
        r.dynamic_energy_threshold = True
        try:
            audio = r.listen(source, timeout=3)  # Reduced timeout to 3 seconds
    try:
        query = r.recognize_google(audio)
        print(f"You: {query}")
        return query
    except sr.UnknownValueError:
                speak("Sorry, I didn't catch that.")
        return None
    except sr.RequestError:
        speak("Sorry, there's a problem with the speech service.")
                return None
        except sr.WaitTimeoutError:
        return None


# 🌦 Get weather function

def get_weather(city="Kochi"):
    api_key = "691c14d40ca41261a24546a5ed159d6b"  # Replace with your actual API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url)
        data = response.json()

        if data["cod"] != 200:
            return "Sorry, I couldn't find the weather for that location."

        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]

        return f"The weather in {city} is {weather_desc} with a temperature of {temp}°C. It feels like {feels_like}°C."

    except Exception as e:
        return "Sorry, I couldn't fetch the weather information right now."
    

def open_app(app_name):
    app_paths = {
        "vs code": r"C:\Users\babhi\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "whatsapp": r"C:\Users\babhi\AppData\Local\WhatsApp\WhatsApp.exe",
        "cursor": r"C:\Users\babhi\AppData\Local\Programs\Cursor\Cursor.exe",
        "notepad": "notepad.exe",
        "capcut": r"C:\Program Files\CapCut\CapCut.exe",
        "camera": "start microsoft.windows.camera:"
    }
    
    try:
        if app_name.lower() in app_paths:
            path = app_paths[app_name.lower()]
            if path.startswith("start "):
                os.system(path)
            else:
                subprocess.Popen(path)
            speak(f"Opening {app_name} for you!")
            else:
            speak(f"Sorry, I don't know how to open {app_name}.")
    except Exception as e:
        print(f"Error opening {app_name}: {e}")
        speak(f"Sorry, I couldn't open {app_name}.")

def open_essentials():
    speak("Opening your essential apps...")

    web_apps = {
                "GitHub": "https://github.com",
                "ChatGPT": "https://chat.openai.com",
                "Canva": "https://www.canva.com",
                "Figma": "https://www.figma.com",
        "YouTube": "https://youtube.com"
    }
    
    desktop_apps = {
        "vs code": r"C:\Users\babhi\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "whatsapp": r"C:\Users\babhi\AppData\Local\WhatsApp\WhatsApp.exe",
      
        "notepad": "notepad.exe"
    }
    
    # Open web apps
    for name, url in web_apps.items():
                try:
                    speak(f"Opening {name}...")
                    webbrowser.open(url)
                except Exception as e:
            speak(f"Couldn't open {name}.")
                    print(f"Error opening {name}: {e}")

    # Open desktop apps
    for name, path in desktop_apps.items():
        try:
            speak(f"Opening {name}...")
            if path.startswith("start "):
                os.system(path)
            else:
                subprocess.Popen(path)
        except Exception as e:
            speak(f"Couldn't open {name}.")
            print(f"Error opening {name}: {e}")

def system_control(command):
    try:
        if "shutdown" in command:
            speak("Shutting down the computer in 1 minute.")
            os.system("shutdown /s /t 60")
        elif "restart" in command:
            speak("Restarting the computer in 1 minute.")
            os.system("shutdown /r /t 60")
        elif "lock" in command:
            speak("Locking the computer.")
            ctypes.windll.user32.LockWorkStation()
        elif "volume up" in command:
            pyautogui.press("volumeup")
            speak("Volume increased.")
        elif "volume down" in command:
            pyautogui.press("volumedown")
            speak("Volume decreased.")
        elif "mute" in command:
            pyautogui.press("volumemute")
            speak("Volume muted.")
    except Exception as e:
        print(f"Error in system control: {e}")
        speak("Sorry, I couldn't perform that action.")

def tell_joke():
    try:
        joke = pyjokes.get_joke()
        speak(joke)
    except Exception as e:
        print(f"Error telling joke: {e}")
        speak("Sorry, I couldn't think of a joke right now.")

def get_system_info():
    try:
        # Get CPU information
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        cpu_count = psutil.cpu_count()
        
        # Get memory information
        memory = psutil.virtual_memory()
        memory_total = round(memory.total / (1024**3), 2)  # Convert to GB
        memory_used = round(memory.used / (1024**3), 2)
        memory_percent = memory.percent
        
        # Get disk information
        disk = psutil.disk_usage('/')
        disk_total = round(disk.total / (1024**3), 2)
        disk_used = round(disk.used / (1024**3), 2)
        disk_percent = disk.percent
        
        # Get battery information
        battery = psutil.sensors_battery()
        battery_info = ""
        if battery:
            battery_info = f"Battery is at {battery.percent}%"
            if battery.power_plugged:
                battery_info += " and is charging."
            else:
                battery_info += f" with {round(battery.secsleft/60)} minutes remaining."
        
        # Get current time in Indian timezone
        indian_time = datetime.now(pytz.timezone('Asia/Kolkata'))
        time_info = f"Current time in India is {indian_time.strftime('%I:%M %p')}"
        
        # Generate detailed system report
        system_report = f"""
        {time_info}
        CPU Usage: {cpu_percent}%
        CPU Frequency: {cpu_freq.current:.2f} MHz
        CPU Cores: {cpu_count}
        Memory: {memory_used}GB used out of {memory_total}GB ({memory_percent}%)
        Disk: {disk_used}GB used out of {disk_total}GB ({disk_percent}%)
        {battery_info}
        """
        
        # Use Gemini to analyze and explain the system status
        try:
            response = model.generate_content(f"Analyze this system report and explain it in simple terms: {system_report}")
            speak(response.text)
        except Exception as e:
            print(f"Error getting Gemini response: {e}")
            speak(system_report)
            
    except Exception as e:
        print(f"Error getting system info: {e}")
        speak("Sorry, I couldn't get the system information.")

def get_time_info():
    try:
        from datetime import datetime
        import pytz
        indian_time = datetime.now(pytz.timezone('Asia/Kolkata'))
        time_str = indian_time.strftime('%I:%M %p')
        date_str = indian_time.strftime('%A, %B %d, %Y')
        
        time_info = f"The current time in India is {time_str} on {date_str}"
        speak(time_info)
    except Exception as e:
        print(f"Error getting time info: {e}")
        speak("Sorry, I couldn't get the time information.")

def update_context(user_input, response):
    """Update conversation history and context"""
    conversation_history.append({
        "user": user_input,
        "assistant": response
    })
    
    # Extract and store important context
    if "my name is" in user_input.lower():
        name = user_input.lower().split("my name is")[-1].strip()
        user_context["name"] = name
    
    if "i live in" in user_input.lower():
        location = user_input.lower().split("i live in")[-1].strip()
        user_context["location"] = location

def get_contextual_response(user_input):
    """Generate response based on conversation history and context"""
    context = ""
    
    # Add user's name if known
    if "name" in user_context:
        context += f"User's name is {user_context['name']}. "
    
    # Add location if known
    if "location" in user_context:
        context += f"User lives in {user_context['location']}. "
    
    # Add recent conversation history
    if conversation_history:
        context += "Recent conversation: "
        for conv in conversation_history:
            context += f"User said: {conv['user']}. Assistant replied: {conv['assistant']}. "
    
    return context

def set_reminder(reminder_text, time_input):
    try:
        # Convert time input to seconds
        if isinstance(time_input, str):
            # Extract numbers from the string
            numbers = re.findall(r'\d+', time_input)
            if not numbers:
                speak("Please specify a valid time duration.")
                return "Failed to set reminder: Invalid time format"
            
            time_value = int(numbers[0])
            
            if "second" in time_input.lower():
                seconds = time_value
            elif "minute" in time_input.lower():
                seconds = time_value * 60
            elif "hour" in time_input.lower():
                seconds = time_value * 3600
            else:
                # Default to seconds if no unit specified
                seconds = time_value
        else:
            seconds = int(time_input)

        # Add reminder using reminder manager
        if reminder_manager.add_reminder(reminder_text, seconds):
            return f"Reminder set: {reminder_text} in {seconds} seconds"
        else:
            return "Failed to set reminder"
            
            except Exception as e:
        print(f"Error setting reminder: {e}")
        return "Sorry, I couldn't set the reminder."

# 🚀 Main chat function
def chat():
    speak("What can I do for you today?")
    while True:
        user_input = listen()

        if not user_input:
            continue

        command = user_input.lower()
        
        # Get contextual information
        context = get_contextual_response(user_input)

        if "stop" in command:
            speak("Goodbye! Take care.")
            break

        elif any(phrase in command for phrase in ["what time is it", "current time", "time now", "tell me the time"]):
            response = get_time_info()
            update_context(user_input, response)

        elif "system info" in command or "how is my computer" in command:
            response = get_system_info()
            update_context(user_input, response)

        elif "remind me" in command or "remember me" in command:
            try:
                # Extract reminder text and time
                reminder_parts = command.split("in", 1)
                if len(reminder_parts) > 1:
                    reminder_text = reminder_parts[0].replace("remind me", "").replace("remember me", "").strip()
                    time_input = reminder_parts[1].strip()
                else:
                    speak("What should I remind you about?")
                    reminder_text = listen()
                    if not reminder_text:
                        continue
                    speak("In how much time? (e.g., 2 seconds, 5 minutes, 1 hour)")
                    time_input = listen()
                    if not time_input:
                        continue

                response = set_reminder(reminder_text, time_input)
                speak(response)
                update_context(user_input, response)
            except Exception as e:
                print(f"Error in reminder handling: {e}")
                speak("Sorry, I couldn't set the reminder.")

        elif any(word in command for word in ["shutdown", "restart", "lock", "volume"]):
            response = system_control(command)
            update_context(user_input, response)

        elif "tell me a joke" in command:
            response = tell_joke()
            update_context(user_input, response)

        elif "open essentials" in command:
            response = "Opening your essential apps"
            open_essentials()
            update_context(user_input, response)

        elif "open" in command:
            # Check if it's a web URL or desktop app
            if any(word in command for word in ["youtube", "github", "chatgpt", "canva", "figma"]):
                # Handle web URLs
                if "youtube" in command:
                    response = "Opening YouTube for you!"
            webbrowser.open("https://youtube.com")
                elif "github" in command:
                    response = "Opening GitHub for you!"
                    webbrowser.open("https://github.com")
                elif "chatgpt" in command:
                    response = "Opening ChatGPT for you!"
                    webbrowser.open("https://chat.openai.com")
                elif "canva" in command:
                    response = "Opening Canva for you!"
                    webbrowser.open("https://www.canva.com")
                elif "figma" in command:
                    response = "Opening Figma for you!"
                    webbrowser.open("https://www.figma.com")
            else:
                # Handle desktop apps
                app_name = command.replace("open", "").strip()
                response = f"Opening {app_name} for you!"
                open_app(app_name)
            update_context(user_input, response)

        elif "play" in command or "music" in command or "song" in command:
            song_name = command.replace("play", "").replace("music", "").strip()
            if not song_name:
                speak("What song would you like to play?")
                song_name = listen()

            if song_name:
                response = f"Playing {song_name} on YouTube..."
                try:
                    pywhatkit.playonyt(song_name)
                except Exception as e:
                    response = "Sorry, couldn't play that song."
                    print("Error:", e)
            else:
                response = "Sorry, I didn't catch the song name."
            update_context(user_input, response)

        elif "weather" in command:
            speak("Which city's weather would you like to know?")
            city = listen()
            if city:
                response = get_weather(city)
                speak(response)
            else:
                response = "Sorry, I didn't catch the city name."
                speak(response)
            update_context(user_input, response)

        elif any(word in command for word in ["tell me about", "explain", "what is", "how to", "story", "history"]):
            try:
                # Add context to the query
                query_with_context = f"{context} {user_input}"
                response = model.generate_content(query_with_context)
                cleaned_response = strip_markdown(response.text)
                speak(cleaned_response, is_detailed=True)
                update_context(user_input, cleaned_response)
                except Exception as e:
                print("Error:", e)
                response = "Sorry, I couldn't process that request right now."
                speak(response)
                update_context(user_input, response)

        else:
            try:
                # Add context to the query
                query_with_context = f"{context} {user_input}"
                response = model.generate_content(query_with_context)
                cleaned_response = strip_markdown(response.text)
                speak(cleaned_response, is_detailed=True)
                update_context(user_input, cleaned_response)
            except Exception as e:
                print("Error:", e)
                response = "Sorry, I couldn't process that request right now."
                speak(response)
                update_context(user_input, response)

def goodbye():
    farewells = [
        "See you later!",
        "Take care!",
        "Goodbye!",
        "I'll be here when you need me!"
    ]
    speak(random.choice(farewells))


# Start the app
if __name__ == "__main__":
    speak("Jarvis activated. I'm ready to assist you.")
    while True:
        print("Listening...")
        user_input = listen()
        
        if user_input:
            if "stop" in user_input.lower():
                speak("Goodbye! Take care.")
                break
            else:
                chat()
