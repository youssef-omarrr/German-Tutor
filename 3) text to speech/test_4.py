import pyttsx3

engine = pyttsx3.init()
for voice in engine.getProperty('voices'):
    print(voice.id, voice.name, voice.languages)

engine.setProperty('voice', 'Hedda')  # German female example
engine.say("Guten Tag!, i am a robot")
engine.runAndWait()
