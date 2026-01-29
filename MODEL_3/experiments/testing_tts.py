from audio import tts
from LLM import response_formatter


if __name__ == "__main__":
    
    # Example 1: Correction with markdown
    print("\n" + "="*70)
    print("EXAMPLE 1: Formatted Correction")
    print("="*70)

    # Test cases
    plain_text = '''### Great Effort!
Your sentence, *Ich habe gestern ins Kino gegangen*, is almost perfect! The only thing to tweak is the verb "gegangen". Since "gehen" (to go) is a motion verb, it uses the verb "sein" (to be) in the perfect tense, not "haben".

So, the corrected sentence would be: *Ich bin gestern ins Kino gegangen*. Think of it like this: when talking about moving from one place to another, German uses "sein" to show that change in location. You're doing fantastic, keep it up!
Some other ways to say this could be:
- *Ich ging gestern ins Kino* (using the simple past for a completed action)
- *Gestern bin ich ins Kino gegangen* (changing the word order for emphasis)
Keep practicing, and you'll get the hang of these verb patterns in no time!'''

    clean_text = response_formatter._remove_md(plain_text)
    
    
    print(clean_text)
    
    mtts = tts.EdgeTTS(voice="de-DE-KatjaNeural")
    mtts.speak(clean_text)
    
