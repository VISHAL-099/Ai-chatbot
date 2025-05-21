import os
import speech_recognition as sr
import pyttsx3

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Adjust speed if needed

def set_microsoft_heera_voice():
    """Sets the voice to Microsoft Heera (Indian female voice) if available."""
    voices = engine.getProperty('voices')

    for voice in voices:
        if "heera" in voice.id.lower():  # Check if Heera is available
            engine.setProperty('voice', voice.id)
            print(f"Using Microsoft Heera voice: {voice.name}")
            return

    print("Microsoft Heera voice not found. Using default voice.")

# Set Microsoft Heera voice
set_microsoft_heera_voice()

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
    system_apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
        "powerpoint": "powerpnt.exe",
        "chrome": "chrome.exe",
        "edge": "msedge.exe",
        "firefox": "firefox.exe",
        "vs code": "code.exe",
        "command prompt": "cmd.exe",
        "task manager": "taskmgr.exe",
        "settings": "ms-settings:",
        "control panel": "control.exe",
        "paint": "mspaint.exe",
        "file explorer": "explorer.exe"
    }

    if name in system_apps:
        try:
            os.startfile(system_apps[name])
            speak(f"Opening {name}")
        except Exception as e:
            speak(f"Could not open {name}. Error: {e}")
        return

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

def find_file_or_folder(name, drives=["C:\\", "D:\\", "E:\\"]):
    """Searches for a file or folder in the specified drives."""
    speak(f"Searching for {name}. Please wait...")

    for drive in drives:
        for root, dirs, files in os.walk(drive):
            if name.lower() in [d.lower() for d in dirs]:  # Check folders
                folder_path = os.path.join(root, name)
                os.startfile(folder_path)
                speak(f"Found and opening folder {name} in {drive}")
                return
            if name.lower() in [f.lower() for f in files]:  # Check files
                file_path = os.path.join(root, name)
                os.startfile(file_path)
                speak(f"Found and opening file {name} in {drive}")
                return

    speak(f"Sorry, I couldn't find {name} in C, D, or E drive.")

def ai_assistant(command):
    """Processes user commands and performs actions accordingly."""
    command = command.lower()

    if "open" in command:
        app_or_folder = command.replace("open", "").strip()
        open_application_or_folder(app_or_folder)
        return

    if "find" in command:
        search_item = command.replace("find", "").strip()
        find_file_or_folder(search_item)
        return

    if "good bye" in command or "exit" in command:
        speak("Goodbye! Have a great day.")
        exit()

    speak("Sorry, I didn't understand that.")

# Greet and wait for command
speak("Hello! How can I assist you?")
while True:
    user_input = recognize_speech()
    if user_input:
        ai_assistant(user_input)
