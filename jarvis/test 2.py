import os
import subprocess
import speech_recognition as sr
import pyttsx3

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak(text):
    """Converts text to speech."""
    engine.say(text)
    engine.runAndWait()

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

def open_application_or_folder(name):
    """Opens an application, system tool, or folder based on the command."""
    # Common applications and system tools
    system_apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
        "powerpoint": "powerpnt.exe",
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "vs code": "code.exe",
        "command prompt": "cmd.exe",
        "task manager": "taskmgr.exe",
        "settings": "ms-settings:",
        "control panel": "control.exe"
    }

    # Check if it's a known application
    if name in system_apps:
        try:
            os.startfile(system_apps[name])
            speak(f"Opening {name}")
        except Exception as e:
            speak(f"Could not open {name}. Error: {e}")
        return

    # Check if it's a folder (Documents, Downloads, etc.)
    folder_paths = {
        "documents": os.path.expanduser("~/Documents"),
        "downloads": os.path.expanduser("~/Downloads"),
        "desktop": os.path.expanduser("~/Desktop"),
        "pictures": os.path.expanduser("~/Pictures"),
        "videos": os.path.expanduser("~/Videos"),
        "music": os.path.expanduser("~/Music"),
        "c drive": "C:\\",
        "d drive": "D:\\",
        "e drive": "E:\\"
    }

    if name in folder_paths:
        folder_path = folder_paths[name]
        if os.path.exists(folder_path):
            os.startfile(folder_path)
            speak(f"Opening {name}")
        else:
            speak(f"The folder {name} does not exist.")
        return

    speak(f"Sorry, I couldn't find an application or folder named {name}.")

def ai_assistant(command):
    """Processes user commands and performs actions accordingly."""
    command = command.lower()

    if "open" in command:
        app_or_folder = command.replace("open", "").strip()
        open_application_or_folder(app_or_folder)
        return

    if "good bye" in command or "exit" in command:
        speak("Goodbye! Have a great day.")
        exit()

    speak("Sorry, I didn't understand that.")

# Greet and wait for command
speak("Hello! What would you like me to open?")
while True:
    user_input = recognize_speech()
    if user_input:
        ai_assistant(user_input)
