import subprocess
import sys

def test_jarvis_imports():
    try:
        import pyttsx3
        import speech_recognition as sr
        import ollama
        print("✅ All imports OK")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)

def test_ollama_connection():
    try:
        import ollama
        response = ollama.chat(model='mistral', messages=[{'role': 'user', 'content': 'Say OK'}])
        if "OK" in response['message']['content']:
            print("✅ Ollama responds")
        else:
            print("⚠️ Ollama responded but not as expected")
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_jarvis_imports()
    test_ollama_connection()