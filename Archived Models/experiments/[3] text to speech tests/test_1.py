from gtts import gTTS
import playsound

text = "Hello! Wie geht es dir heute? this is just a test"
tts = gTTS(text, lang='de')  # Works even with mixed English/German text
tts.save("output.mp3")
playsound.playsound("output.mp3")
