import json
import os
import speech_recognition as sr
import ollama
import subprocess
import pyttsx3
from datetime import datetime

MEMORY_FILE = "memory_stable.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

memory = load_memory()

# --- Голос с перезапуском движка при ошибке ---
engine = None

def get_engine():
    global engine
    try:
        if engine is None:
            engine = pyttsx3.init()
            engine.setProperty('rate', 170)
            engine.setProperty('volume', 0.9)
            voices = engine.getProperty('voices')
            for v in voices:
                if "male" in v.name.lower() or "david" in v.name.lower():
                    engine.setProperty('voice', v.id)
                    break
        return engine
    except:
        return None

def speak(text):
    print(f"🤖 {text}")
    eng = get_engine()
    if eng:
        try:
            eng.say(text)
            eng.runAndWait()
        except:
            # если упало — пробуем пересоздать движок
            global engine
            engine = None
            eng = get_engine()
            if eng:
                try:
                    eng.say(text)
                    eng.runAndWait()
                except:
                    pass

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        r.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = r.listen(source, timeout=5)
        except sr.WaitTimeoutError:
            return ""
    try:
        text = r.recognize_google(audio, language="en-US")
        print(f"📝 You said: {text}")
        return text.lower()
    except:
        return ""

def ask_ollama(prompt, context=""):
    full_prompt = f"Answer in 1-2 short sentences. Context: {context}\nUser: {prompt}\nJARVIS:"
    try:
        response = ollama.chat(model='mistral', messages=[{'role': 'user', 'content': full_prompt}])
        return response['message']['content']
    except Exception as e:
        return f"Error: {e}"

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return str(e)

def main():
    speak("JARVIS activated. I am listening.")
    while True:
        command = listen()
        if not command:
            continue
        if "exit" in command or "goodbye" in command:
            speak("Goodbye, sir.")
            break

        memory.append({"role": "user", "content": command, "time": str(datetime.now())})
        context = "\n".join([m["content"] for m in memory[-5:]])

        if command.startswith("!"):
            result = run_command(command[1:])
        else:
            result = ask_ollama(command, context)

        memory.append({"role": "assistant", "content": result, "time": str(datetime.now())})
        save_memory(memory)
        speak(result)

if __name__ == "__main__":
    main()