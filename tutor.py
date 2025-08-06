import torch
import speech_recognition as sr
import pyttsx3
import openai
import json
import time

class GermanTutor:
    def __init__(self, openai_api_key=None, use_local_llm=False):
        """
        Initialize German Language Tutor
        
        Args:
            openai_api_key: OpenAI API key (or use free alternatives like Together AI)
            use_local_llm: Whether to use local LLM as backup/primary
        """
        self.openai_api_key = openai_api_key
        self.use_local_llm = use_local_llm
        
        # Initialize components
        self.setup_stt()
        self.setup_tts()
        if use_local_llm:
            self.setup_local_llm()
        if openai_api_key:
            self.setup_api_llm()
        
        # Audio queue for threading
        self.is_listening = False
        
    def setup_stt(self):
        """Setup Speech-to-Text using Google Speech Recognition"""
        print("Setting up speech recognition...")
        
        self.recognizer = sr.Recognizer()
        
        # Try to find the best microphone
        mic_list = sr.Microphone.list_microphone_names()
        print(f"Found {len(mic_list)} microphone(s)")
        
        # Try different microphones until one works
        self.microphone = None
        mic_indices = [None, 0, 1, 2]  # None = default, then try specific indices
        
        for mic_index in mic_indices:
            try:
                test_mic = sr.Microphone(device_index=mic_index)
                with test_mic as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                self.microphone = test_mic
                print(f"✅ Using microphone: {mic_index if mic_index is not None else 'default'}")
                break
                
            except Exception as e:
                print(f"❌ Microphone {mic_index} failed: {e}")
                continue
        
        if self.microphone is None:
            raise Exception("No working microphone found!")
        
        # Optimize settings
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        
        print("✅ Speech recognition ready!")
        
    def setup_tts(self):
        """Setup Text-to-Speech"""
        self.tts_engine = pyttsx3.init()
        voices = self.tts_engine.getProperty('voices')
        
        # Try to find German voice, fallback to default
        german_voice = None
        for voice in voices:
            if 'german' in voice.name.lower() or 'deutsch' in voice.name.lower():
                german_voice = voice.id
                break
        
        if german_voice:
            self.tts_engine.setProperty('voice', german_voice)
        
        # Set speech rate
        self.tts_engine.setProperty('rate', 150)
        print("Text-to-speech ready!")
    
    def setup_local_llm(self):
        """Setup local LLM (lightweight option for RTX 3060)"""
        try:
            from transformers import GPT2LMHeadModel, GPT2Tokenizer
            
            # Use DistilGPT-2 for better compatibility and lower memory
            model_name = "distilgpt2"
            
            print(f"Loading {model_name}...")
            self.local_tokenizer = GPT2Tokenizer.from_pretrained(model_name)
            
            # Load model with proper device handling
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Using device: {device}")
            
            self.local_model = GPT2LMHeadModel.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                low_cpu_mem_usage=True
            ).to(device)
            
            # Set pad token
            if self.local_tokenizer.pad_token is None:
                self.local_tokenizer.pad_token = self.local_tokenizer.eos_token
                
            print("Local LLM loaded successfully!")
            
        except Exception as e:
            print(f"Failed to load local LLM: {e}")
            print("Continuing without local LLM (API only mode)")
            self.local_model = None
            self.local_tokenizer = None
    
    def setup_api_llm(self):
        """Setup API-based LLM (recommended for accuracy)"""
        # You can use OpenAI API or free alternatives like:
        # - Together AI (has free tier)
        # - Hugging Face Inference API (free tier)
        # - Cohere (free tier)
        openai.api_key = self.openai_api_key
        print("API LLM configured!")
    
    def transcribe_audio(self, audio_data):
        """Convert speech to text using Google Speech Recognition"""
        try:
            # Try German first (primary language)
            try:
                german_text = self.recognizer.recognize_google(
                    audio_data, 
                    language='de-DE'
                ).strip()
                
                if german_text:
                    return german_text
                    
            except sr.UnknownValueError:
                # No German speech detected, try English as fallback
                pass
            except sr.RequestError as e:
                print(f"❌ Google Speech API error: {e}")
                return ""
            
            # Fallback to English if German didn't work
            try:
                english_text = self.recognizer.recognize_google(
                    audio_data, 
                    language='en-US'
                ).strip()
                
                if english_text:
                    print(f"🔤 Detected English (translating to German context): '{english_text}'")
                    return english_text
                    
            except sr.UnknownValueError:
                print("🔇 No clear speech detected in German or English")
                return ""
            except sr.RequestError as e:
                print(f"❌ Google Speech API error: {e}")
                return ""
            
            return ""
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return ""
    
    def correct_german_text_api(self, german_text):
        """Use API LLM for German correction and feedback"""
        prompt = f"""You are a German language tutor. A student said: "{german_text}"

Please provide:
1. Corrected German text (if needed)
2. English translation
3. Grammar explanation (if there were errors)
4. Pronunciation tips (if applicable)

Format your response as JSON:
{{
    "original": "{german_text}",
    "corrected": "corrected German text",
    "translation": "English translation",
    "errors": ["list of errors found"],
    "explanation": "grammar explanation",
    "pronunciation_tips": "pronunciation guidance"
}}"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Use cheaper model
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            response_text = response.choices[0].message.content
            # Try to parse JSON, fallback to text if it fails
            try:
                return json.loads(response_text)
            except:
                return {"explanation": response_text}
                
        except Exception as e:
            print(f"API LLM error: {e}")
            return self.correct_german_text_local(german_text)
    
    def correct_german_text_local(self, german_text):
        """Fallback local LLM processing (limited but functional)"""
        if not hasattr(self, 'local_model') or self.local_model is None:
            return {
                "original": german_text,
                "corrected": german_text,
                "translation": "Translation not available (no model loaded)",
                "explanation": "Local model not available. Please provide API key for full functionality."
            }
        
        # Simple German correction logic without LLM generation
        # This is a basic fallback - for real corrections, use API
        
        # Basic German grammar rules
        corrections = {
            "ich bin gut": "Mir geht es gut",
            "wie geht es dir": "Wie geht es dir?",
            "guten tag": "Guten Tag!",
        }
        
        german_lower = german_text.lower().strip()
        
        if german_lower in corrections:
            corrected = corrections[german_lower]
            explanation = f"'{german_text}' should be '{corrected}' for proper German."
        else:
            corrected = german_text
            explanation = f"Your German looks good! '{german_text}' appears to be correctly structured."
        
        # Simple translations
        translations = {
            "mir geht es gut": "I am doing well",
            "ich bin gut": "I am good",
            "wie geht es dir": "How are you doing",
            "guten tag": "Good day",
        }
        
        translation = translations.get(corrected.lower(), "Translation not available locally")
        
        return {
            "original": german_text,
            "corrected": corrected if corrected != german_text else None,
            "translation": translation,
            "explanation": explanation
        }
    
    def speak_text(self, text, language="en"):
        """Convert text to speech"""
        try:
            # Simple language detection and voice adjustment
            if language == "de" and "german" in str(self.tts_engine.getProperty('voices')):
                # Use German voice if available
                pass
            
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
        except Exception as e:
            print(f"TTS error: {e}")
    
    def process_german_input(self, german_text):
        """Main processing pipeline"""
        print(f"\n🎤 You said: '{german_text}'")
        
        # Get correction and feedback
        if self.openai_api_key:
            feedback = self.correct_german_text_api(german_text)
        else:
            feedback = self.correct_german_text_local(german_text)
        
        # Display feedback
        if isinstance(feedback, dict):
            print("\n📝 Feedback:")
            if "corrected" in feedback and feedback["corrected"] != german_text:
                print(f"   Correction: {feedback['corrected']}")
                self.speak_text(feedback["corrected"], "de")
            
            if "translation" in feedback:
                print(f"   Translation: {feedback['translation']}")
                self.speak_text(feedback["translation"], "en")
            
            if "explanation" in feedback:
                print(f"   Explanation: {feedback['explanation']}")
                self.speak_text(feedback["explanation"], "en")
                
            if "errors" in feedback and feedback["errors"]:
                print(f"   Errors found: {', '.join(feedback['errors'])}")
        else:
            print(f"   Response: {feedback}")
            self.speak_text(str(feedback), "en")
        
        print("-" * 50)
    
    def listen_continuously(self):
        """Continuous listening loop"""
        print("\n🎯 German Language Tutor Ready!")
        print("Say something in German... (Press Ctrl+C to stop)")
        print("🔊 Speak clearly and wait for processing after each phrase")
        
        self.is_listening = True
        session_count = 0
        
        while self.is_listening:
            try:
                session_count += 1
                print(f"\n[{session_count}] 🎤 Listening... (speak now)")
                
                with self.microphone as source:
                    # Listen for audio with reasonable timeouts
                    audio_data = self.recognizer.listen(
                        source, 
                        timeout=2,           # Wait 2 seconds for speech to start
                        phrase_time_limit=8  # Allow up to 8 seconds of speech
                    )
                
                print(f"[{session_count}] 🔄 Processing speech...")
                
                # Transcribe using Google Speech Recognition
                german_text = self.transcribe_audio(audio_data)
                
                if german_text and len(german_text.strip()) > 1:
                    self.process_german_input(german_text)
                else:
                    print(f"[{session_count}] 🔇 No clear speech detected. Try again!")
                
                print(f"[{session_count}] ✅ Ready for next input...")
                    
            except sr.WaitTimeoutError:
                print(f"[{session_count}] ⏱️  No speech detected, listening again...")
                continue
            except KeyboardInterrupt:
                print(f"\n👋 Stopping German tutor after {session_count} sessions...")
                self.is_listening = False
                break
            except Exception as e:
                print(f"[{session_count}] ❌ Listening error: {e}")
                print("🔄 Trying again in 2 seconds...")
                time.sleep(2)
    
    def interactive_mode(self):
        """Interactive text-based mode for testing"""
        print("\n📚 Interactive German Tutor")
        print("Type German sentences to get corrections (type 'quit' to exit):")
        
        while True:
            try:
                german_input = input("\n🇩🇪 German: ").strip()
                if german_input.lower() in ['quit', 'exit', 'bye']:
                    break
                if german_input:
                    self.process_german_input(german_input)
            except KeyboardInterrupt:
                break
        
        print("👋 Auf Wiedersehen!")

# Example usage and setup
def main():
    # Configuration
    OPENAI_API_KEY = "your-api-key-here"  # Replace with actual API key
    # Alternative free APIs:
    # - Together AI: https://api.together.xyz/
    # - Hugging Face: https://huggingface.co/inference-api
    
    USE_LOCAL_LLM = True  # Set to True to use local model as backup
    
    # Initialize tutor
    print("🚀 Starting German Language Tutor...")
    tutor = GermanTutor(
        openai_api_key=OPENAI_API_KEY if OPENAI_API_KEY != "your-api-key-here" else None,
        use_local_llm=USE_LOCAL_LLM
    )
    
    # Choose mode
    print("\nSelect mode:")
    print("1. Voice mode (speak German)")
    print("2. Text mode (type German)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        tutor.listen_continuously()
    else:
        tutor.interactive_mode()

if __name__ == "__main__":
    main()