import pyttsx3
import speech_recognition as sr
from langdetect import detect
from autocorrect import Speller  # For auto-correction of text
import ollama

class AIAssitant:
    def __init__(self, use_voice=True):
        self.use_voice = use_voice
        self.current_language = "en"  # Force English only
        self.model = self.select_model()  # Ask user which model to use

        # Voice engine
        if use_voice:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', voices[1].id)  # Female voice
            self.engine.setProperty('rate', 150)

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Initialize the autocorrect speller
        self.speller = Speller()

    def list_models(self):
        """List available models from Ollama"""
        try:
            models = ollama.list()
            return [model["model"] if "model" in model else model.get("name", "unknown") for model in models.get("models", [])]
        except Exception as e:
            print(f"⚠️ Could not list models: {e}")
            return []

    def select_model(self):
        models = self.list_models()
        if not models:
            print("⚠️ No models found. Using fallback: llama3.1:latest")
            return "llama3.1:latest"
        
        print("🧠 Available models:")
        for i, model in enumerate(models, 1):
            print(f"{i}. {model}")

        choice = input("Select a model by number (default 1): ")
        try:
            index = int(choice.strip()) - 1
            selected_model = models[index]
        except:
            selected_model = models[0]
            print(f"❕ Defaulting to: {selected_model}")
        
        print(f"✅ Model selected: {selected_model}")
        return selected_model

    def detect_language(self, text):
        try:
            return "ta" if detect(text) == "ta" else "en"
        except:
            return "en"

    def get_ai_response(self, text):
        prompt = f"Give a short, friendly and clear response in English only. User: {text}"

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.6}
            )
            return response['message']['content'].strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def speak(self, text):
        print(f"AI: {text}")
        if self.use_voice:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Error in speech synthesis: {str(e)}")

    def listen(self):
        with self.microphone as source:
            print("\n🎤 Speak now... (Please speak clearly and completely)")

            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source)

            # Listen for a longer time to capture more complete sentences
            try:
                audio = self.recognizer.listen(source, timeout=10)  # Increased timeout for more time to speak
                text = self.recognizer.recognize_google(audio, language="en-US")
                
                # Correct spelling errors
                corrected_text = self.speller(text)

                print(f"You: {corrected_text}")
                return corrected_text
            except sr.UnknownValueError:
                print("Sorry, I couldn't understand. Could you repeat?")
                return ""
            except sr.RequestError:
                print("Sorry, there was an error with the speech recognition service.")
                return ""

    def start(self):
        self.speak("Hello! I'm your AI assistant. Ask me anything.")

        while True:
            user_input = self.listen()
            if not user_input:
                self.speak("Sorry, can you repeat that?")
                continue

            # Exit commands
            if any(cmd in user_input.lower() for cmd in ['exit', 'stop', 'quit', 'bye']):
                self.speak("Goodbye!")
                break

            # Get AI response
            response = self.get_ai_response(user_input)

            # If AI response is unclear, ask user to rephrase
            if "I'm not sure" in response or "I don't know" in response:
                self.speak("Sorry, I couldn't understand that. Could you rephrase?")
            else:
                self.speak(response)

if __name__ == "__main__":
    print("🚀 Starting Tamil AI Assistant...")
    assistant = AIAssitant(use_voice=True)
    assistant.start()
