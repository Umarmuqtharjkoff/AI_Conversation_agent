import pyttsx3
import speech_recognition as sr
from langdetect import detect
from autocorrect import Speller
import ollama

class AIAssistant:
    def __init__(self, use_voice=True):
        self.use_voice = use_voice
        self.model = self.select_model()
        
        if use_voice:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', voices[1].id)  # Female voice
            self.engine.setProperty('rate', 150)
        
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.speller = Speller()

    def list_models(self):
        try:
            models = ollama.list()
            return [model.get("model", model.get("name", "unknown")) for model in models.get("models", [])]
        except Exception as e:
            print(f"[!] Could not list models: {e}")
            return []

    def select_model(self):
        models = self.list_models()
        if not models:
            print("[!] No models found. Defaulting to llama3:latest")
            return "llama3:latest"
        
        print("Available models:")
        for i, model in enumerate(models, 1):
            print(f"{i}. {model}")

        choice = input("Select a model by number (default 1): ")
        try:
            selected_model = models[int(choice.strip()) - 1]
        except:
            selected_model = models[0]
            print(f"[i] Using default model: {selected_model}")
        
        return selected_model

    def get_ai_response(self, text):
        prompt = f"Give a short, friendly, and clear response in English only. User: {text}"
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.6}
            )
            return response['message']['content'].strip()
        except Exception as e:
            return f"[!] Error: {str(e)}"

    def speak(self, text):
        print(f"AI: {text}")
        if self.use_voice:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"[!] Text-to-Speech Error: {str(e)}")

    def listen(self):
        with self.microphone as source:
            print("\n🎤 Listening... (speak clearly)")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=10)
                text = self.recognizer.recognize_google(audio, language="en-US")
                corrected_text = self.speller(text)
                print(f"You: {corrected_text}")
                return corrected_text
            except sr.UnknownValueError:
                print("Sorry, I didn't catch that.")
                return ""
            except sr.RequestError:
                print("Error connecting to speech service.")
                return ""

    def start(self):
        self.speak("Hello! I'm your AI assistant. Ask me anything.")
        while True:
            user_input = self.listen()
            if not user_input:
                self.speak("Could you please repeat?")
                continue

            if any(cmd in user_input.lower() for cmd in ['exit', 'stop', 'quit', 'bye']):
                self.speak("Goodbye!")
                break

            response = self.get_ai_response(user_input)

            if "I'm not sure" in response or "I don't know" in response:
                self.speak("I'm not quite sure about that. Could you rephrase?")
            else:
                self.speak(response)

if __name__ == "__main__":
    print("🚀 Starting AI Assistant...")
    assistant = AIAssistant(use_voice=True)
    assistant.start()
