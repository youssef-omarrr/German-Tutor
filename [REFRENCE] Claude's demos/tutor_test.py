#!/usr/bin/env python3
"""
Quick test for the updated German tutor
"""

def test_imports():
    """Test if all required modules can be imported"""
    print("🔄 Testing imports...")
    
    try:
        import speech_recognition as sr
        print("✅ speech_recognition")
    except ImportError as e:
        print(f"❌ speech_recognition: {e}")
        return False
    
    try:
        import pyttsx3
        print("✅ pyttsx3")
    except ImportError as e:
        print(f"❌ pyttsx3: {e}")
        return False
    
    try:
        import torch
        print("✅ torch")
    except ImportError as e:
        print(f"❌ torch: {e}")
        return False
    
    return True

def test_microphone():
    """Test microphone functionality"""
    print("\n🔄 Testing microphone...")
    
    try:
        import speech_recognition as sr
        
        # List microphones
        mic_list = sr.Microphone.list_microphone_names()
        print(f"✅ Found {len(mic_list)} microphones")
        
        # Test default microphone
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
        
        print("✅ Microphone initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False

def test_tts():
    """Test text-to-speech"""
    print("\n🔄 Testing text-to-speech...")
    
    try:
        import pyttsx3
        
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        print(f"✅ Found {len(voices)} TTS voices")
        
        # Quick TTS test
        engine.say("Testing German tutor")
        engine.runAndWait()
        
        print("✅ TTS working")
        return True
        
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False

def test_speech_recognition():
    """Test Google speech recognition"""
    print("\n🔄 Testing speech recognition...")
    print("Say 'hello' when prompted...")
    
    try:
        import speech_recognition as sr
        
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Speak now...")
            audio = r.listen(source, timeout=3, phrase_time_limit=3)
        
        print("🔄 Processing...")
        text = r.recognize_google(audio, language='en-US')
        print(f"✅ Heard: '{text}'")
        
        return True
        
    except sr.WaitTimeoutError:
        print("❌ No speech detected")
        return False
    except sr.UnknownValueError:
        print("❌ Could not understand audio")
        return False
    except Exception as e:
        print(f"❌ Speech recognition failed: {e}")
        return False

def main():
    print("🧪 TESTING UPDATED GERMAN TUTOR")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Microphone", test_microphone),
        ("Text-to-Speech", test_tts)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 All tests passed! Your German tutor should work!")
        
        # Optional speech test
        test_speech = input("\nDo you want to test speech recognition? (y/n): ").lower().strip()
        if test_speech == 'y':
            test_speech_recognition()
        
        print("\n✅ Ready to run: python tutor.py")
        
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install missing packages: pip install speech_recognition pyttsx3")
        print("- Check microphone permissions in Windows settings")
        print("- Try: pip install pyaudio (or pipwin install pyaudio on Windows)")

if __name__ == "__main__":
    main()