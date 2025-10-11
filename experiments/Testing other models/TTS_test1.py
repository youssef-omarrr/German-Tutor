import asyncio
import edge_tts
import playsound


sample_text = (
        "Corrected Sentence: "
        "Auf Wiedersehen Explanation: "
        "The phrase  Auf Wieder  is incomplete the usual farewell is Auf Wiedersehen literally  until we see each other again . "
        "German nouns are capitalized, so Wiedersehen starts with a capital W. "
        "Adding an exclamation mark or a period makes the sentence complete and shows the intended tone. "
        "Alternative Wordings slash Style Improvements: "
        "Alternative one: "
        "Bis später Use this informal goodbye when you expect to see the person later the same day. "
        "Alternative two: "
        "Tschüss A casual and friendly way to say  bye  in everyday conversation. "
        "Alternative three: "
        "Bis bald Means  see you soon,  suitable when you plan to meet again sometime in the near future. "
        "Keep up the great work practicing these common farewells will make your German sound natural "
    )

async def main():
    tts = edge_tts.Communicate(sample_text, "de-DE-KatjaNeural")
    await tts.save("output.mp3")

asyncio.run(main())
playsound.playsound("output.mp3")
