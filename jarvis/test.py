import speech_recognition as sr
import webbrowser
import pyttsx3
import datetime
import pandas as pd
import re
import time
import os
import psutil
import subprocess
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)


def speak(text):
    """Converts text to speech."""
    engine.say(text)
    engine.runAndWait()


def set_female_voice():
    """Sets a female voice if available."""
    voices = engine.getProperty('voices')
    for voice in voices:
        if "female" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            return
    engine.setProperty('voice', voices[1].id)


def greet_user():
    """Greets the user based on the time of the day."""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        greeting = "Good morning, Boss!"
    elif 12 <= hour < 18:
        greeting = "Good afternoon, Boss!"
    else:
        greeting = "Good evening, Boss!"
    speak(f"{greeting} Say 'hey jarvis' to wake me up.")


# Load CSV file into a dictionary
try:
    commands_df = pd.read_csv("commands.csv")
    commands_dict = {command.lower(): link for command, link in zip(commands_df["command"], commands_df["link"])}
except FileNotFoundError:
    commands_dict = {}
    print("Error: 'commands.csv' file not found!")


def extract_keyword(command):
    """Extracts keywords from commands like 'Can you open YouTube'."""
    match = re.search(r"\bopen\s+(.+)", command)
    return match.group(1).strip() if match else None


current_driver = None  # To track the current browser instance


def play_youtube_video(query):
    """Directly opens and plays the first video matching the search query."""
    global current_driver
    speak(f"Playing {query} on YouTube.")

    options = webdriver.ChromeOptions()
    options.add_argument("--start-minimized")

    if current_driver:
        current_driver.quit()

    current_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        current_driver.get("https://www.youtube.com")
        time.sleep(5)
        try:
            accept_button = current_driver.find_element(By.XPATH, '//button[contains(text(), "Accept")]')
            accept_button.click()
        except:
            pass
        search_box = current_driver.find_element(By.NAME, "search_query")
        search_box.send_keys(query)
        search_box.submit()
        first_video = WebDriverWait(current_driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '(//a[@id="video-title"])[1]'))
        )
        first_video.click()
        speak("Playing the first video now.")
    except Exception as e:
        print(f"Error playing video: {e}")
        speak("I couldn't play the video.")


def stop_current_video():
    """Stops the current video by closing the browser."""
    global current_driver
    if current_driver:
        current_driver.quit()
        current_driver = None
        speak("Video stopped.")


def recognize_speech(timeout=10):
    """Captures speech input and converts it into text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1.5)
        try:
            audio = recognizer.listen(source, timeout=timeout)
            command = recognizer.recognize_google(audio)
            print(f"Recognized: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Could not understand the audio.")
            return ""
        except sr.RequestError:
            speak("Network error. Please check your connection.")
            return ""
        except sr.WaitTimeoutError:
            print("Listening timed out. Waiting for speech...")
            return ""


def find_application(app_name):
    """Searches for an installed application on Windows."""
    possible_paths = [
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        "C:\\Users\\{}\\AppData\\Local".format(os.getlogin()),
        "C:\\Users\\{}\\AppData\\Roaming".format(os.getlogin())
    ]

    for path in possible_paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                for dir_name in dirs:
                    if app_name.lower() in dir_name.lower():
                        return os.path.join(root, dir_name)

    return None


def open_application(app_name):
    """Opens an application if found on the system."""
    common_apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
        "powerpoint": "powerpnt.exe",
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "vs code": "code.exe"
    }
 
    if app_name in common_apps:
        try:
            os.startfile(common_apps[app_name])
            speak(f"Opening {app_name}")
            return
        except Exception as e:
            speak(f"Could not open {app_name}. Error: {e}")
            return

    app_path = find_application(app_name)

    if app_path:
        os.startfile(app_path)
        speak(f"Opening {app_name}")
    else:
        speak(f"Application {app_name} not found.")


def ai_assistant(command):
    """Processes user commands and performs actions accordingly."""
    command = command.lower()

    if "find" in command and "on laptop" in command:
        app_name = command.replace("find", "").replace("on laptop", "").replace("and open it", "").strip()
        app_path = find_application(app_name)
        if app_path:
            speak(f"{app_name} is installed on your laptop. Do you want me to open it?")
            user_input = recognize_speech()
            if "yes" in user_input or "open" in user_input:
                open_application(app_name)
            else:
                speak("Okay, not opening the application.")
        else:
            speak(f"Could not find {app_name} installed on your laptop.")
        return

    if "open" in command:
        app_name = command.replace("open", "").strip()
        open_application(app_name)
        return

    youtube_match = re.search(r"(play|search)\s+(.*?)\s+(on\s+youtube|in\s+youtube|in\s+yt)", command)
    if youtube_match:
        video_query = youtube_match.group(2).strip()
        play_youtube_video(video_query)
        return

    if "good bye" in command or "exit" in command:
        speak("Goodbye! Have a great day.")
        exit()

    speak("Sorry, I didn't understand that.")


# Set female voice
set_female_voice()

# Start in sleep mode
greet_user()
wake_word = "start"

while True:
    print("Waiting for the wake word...")
    command = recognize_speech()

    if command and wake_word in command:
        speak("I'm awake! How can I assist you?")

        while True:
            user_input = recognize_speech()
            if user_input:
                if "good bye" in user_input or "exit" in user_input:
                    speak("Goodbye! Have a great day.")
                    exit()
                elif "stop" in user_input:
                    speak("Going to sleep. Say 'start' to wake me up.")
                    break
                else:
                    ai_assistant(user_input)
