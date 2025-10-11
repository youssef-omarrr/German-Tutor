import asyncio
import edge_tts
import playsound

async def main():
    tts = edge_tts.Communicate("Hello! Wie geht es dir? this is just a test", "de-DE-KatjaNeural")
    await tts.save("output.mp3")

asyncio.run(main())
playsound.playsound("output.mp3")
