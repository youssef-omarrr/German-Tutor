import speech_recognition as sr
import whisper
import torch
import tempfile
import os
import time

def test_microphone_basic():
    """Test basic microphone functionality"""
    print("🎤 Testing Basic Microphone Setup...")
    print("-" * 50)
    
    # List available microphones
    print("Available microphones:")
    mic_list = sr.Microphone.list_microphone_names()
    for i, name in enumerate(mic_list):
        print(f"  {i}: {name}")
    
    if not mic_list:
        print("❌ No microphones found!")
        return False
    
    print(f"\n✅ Found {len(mic_list)} microphone(s)")
    return True

def test_whisper_transcription():
    """Test Whisper transcription with microphone input"""
    print("\n🔄 Loading Whisper model...")
    
    # Check CUDA
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # Load Whisper model
    try:
        model = whisper.load_model("tiny", device=device)  # Use tiny for faster testing
        print("✅ Whisper model loaded successfully!")
    except Exception as e:
        print(f"❌ Failed to load Whisper: {e}")
        return None
    
    return model

def live_transcription_test():
    """Live microphone transcription test"""
    print("\n🎯 Live Transcription Test")
    print("=" * 50)
    
    # Setup
    if not test_microphone_basic():
        return
    
    model = test_whisper_transcription()
    if model is None:
        return
    
    # Initialize speech recognition
    recognizer = sr.Recognizer()
    
    # Try different microphones if default fails
    mic_indices = [None, 0, 1]  # None = default, then try index 0, 1
    
    for mic_index in mic_indices:
        try:
            print(f"\n🔄 Trying microphone index: {mic_index if mic_index is not None else 'default'}")
            microphone = sr.Microphone(device_index=mic_index)
            
            # Adjust for ambient noise
            print("🔄 Adjusting for ambient noise...")
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=2)
            
            print("✅ Microphone initialized successfully!")
            break
            
        except Exception as e:
            print(f"❌ Failed with microphone {mic_index}: {e}")
            if mic_index == mic_indices[-1]:  # Last attempt
                print("❌ All microphone attempts failed!")
                return
    
    # Configure recognition settings
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8
    recognizer.phrase_threshold = 0.3
    
    print("\n" + "=" * 50)
    print("🎤 LIVE MICROPHONE TEST")
    print("Speak clearly into your microphone...")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    session_count = 0
    
    while True:
        try:
            session_count += 1
            print(f"\n[{session_count}] 🎤 Listening... (speak now)")
            
            # Listen for audio
            with microphone as source:
                audio_data = recognizer.listen(
                    source,
                    timeout=3,      # Wait 3 seconds for speech
                    phrase_time_limit=8  # Max 8 seconds of speech
                )
            
            print(f"[{session_count}] 🔄 Processing audio...")
            
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio_data.get_wav_data())
                temp_path = tmp_file.name
            
            try:
                # Transcribe with Whisper
                result = model.transcribe(
                    temp_path,
                    language="de",  # German
                    fp16=torch.cuda.is_available()
                )
                
                transcribed_text = result["text"].strip()
                
                if transcribed_text:
                    print(f"[{session_count}] 🎯 German: '{transcribed_text}'")
                    
                    # Also try English transcription for comparison
                    result_en = model.transcribe(temp_path, language="en")
                    english_text = result_en["text"].strip()
                    
                    if english_text and english_text != transcribed_text:
                        print(f"[{session_count}] 🔤 English: '{english_text}'")
                        
                else:
                    print(f"[{session_count}] 🔇 No speech detected")
                    
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
            
            print(f"[{session_count}] ✅ Ready for next input...")
            
        except sr.WaitTimeoutError:
            print(f"[{session_count}] ⏱️  Timeout - no speech detected")
            
        except KeyboardInterrupt:
            print(f"\n\n👋 Test completed after {session_count} attempts!")
            print("Microphone test finished.")
            break
            
        except Exception as e:
            print(f"[{session_count}] ❌ Error: {e}")
            print("🔄 Continuing...")
            time.sleep(1)

def simple_speech_recognition_test():
    """Test using built-in speech recognition (without Whisper)"""
    print("\n🔄 Simple Speech Recognition Test (Google API)")
    print("-" * 50)
    
    recognizer = sr.Recognizer()
    
    try:
        microphone = sr.Microphone()
        
        print("🔄 Adjusting for ambient noise...")
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=2)
        
        print("🎤 Say something... (5 seconds)")
        
        with microphone as source:
            audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=4)
        
        print("🔄 Processing with Google Speech Recognition...")
        
        # Try German first
        try:
            text_de = recognizer.recognize_google(audio_data, language='de-DE')
            print(f"✅ German: '{text_de}'")
        except:
            print("❌ German recognition failed")
        
        # Try English
        try:
            text_en = recognizer.recognize_google(audio_data, language='en-US')
            print(f"✅ English: '{text_en}'")
        except:
            print("❌ English recognition failed")
            
    except Exception as e:
        print(f"❌ Simple recognition failed: {e}")

def main():
    print("🎤 MICROPHONE TEST SCRIPT")
    print("=" * 50)
    
    while True:
        print("\nSelect test:")
        print("1. 🎯 Live transcription (Whisper + Microphone)")
        print("2. 🔍 Simple recognition test (Google API)")
        print("3. 📋 List microphones")
        print("4. ❌ Exit")
        
        try:
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == "1":
                live_transcription_test()
            elif choice == "2":
                simple_speech_recognition_test()
            elif choice == "3":
                test_microphone_basic()
            elif choice == "4":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Please enter 1, 2, 3, or 4")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()