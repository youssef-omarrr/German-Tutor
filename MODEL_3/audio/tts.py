"""
Text-to-Speech using Edge-TTS
Fast, free, high-quality German voices
"""

import edge_tts
import asyncio
from typing import Optional
from rich.console import Console
import tempfile
import os
from pydub import AudioSegment
from pydub.playback import play
import subprocess


class EdgeTTS:
    """
    Text-to-Speech using Microsoft Edge TTS.
    Free, fast, and high quality.
    """
    
    def __init__(
        self,
        voice: str = "de-DE-KatjaNeural",  # German female voice
        rate: str = "+0%",  # Speaking rate
        pitch: str = "+7Hz",  # Pitch adjustment
    ):
        """
        Initialize Edge TTS.
        
        Args:
            voice: Voice ID to use
                German voices:
                - "de-DE-KatjaNeural" (female)
                - "de-DE-ConradNeural" (male)
                - "de-AT-IngridNeural" (Austrian female)
                - "de-CH-LeniNeural" (Swiss female)
            rate: Speaking rate adjustment (e.g., "+10%" faster, "-10%" slower)
            pitch: Pitch adjustment (e.g., "+5Hz" higher, "-5Hz" lower)
        """
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        self.console = Console()
    
    async def _stream_speak(self, text: str):
        """
        Streams audio directly to mpv without saving a file.
        """
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice,
            rate=self.rate,
            pitch=self.pitch
        )

        # Open mpv process to receive audio data via stdin
        # '--no-cache' and '--untied-lirc-interface' help with instant playback
        mpv_command = ["mpv", "--no-cache", "--no-terminal", "--", "-"]
        process = subprocess.Popen(mpv_command, stdin=subprocess.PIPE)

        try:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    process.stdin.write(chunk["data"])
        finally:
            if process.stdin:
                process.stdin.close()
            process.wait()

    def speak(self, text: str):
        """
        Synthesize and play audio immediately using direct streaming.
        """
        if not text:
            return
        
        with self.console.status("[bold green]🔊 Speaking...[/]", spinner="material"):
            try:
                asyncio.run(self._stream_speak(text))
            except Exception as e:
                self.console.print(f"[red]Playback error: {e}[/]")
    
    def _list_voices():
        """
        List all available voices (async).
        Useful for finding voice IDs.
        """
        async def _list():
            voices = await edge_tts.VoicesManager.create()
            voices_list = voices.voices
            
            # Filter German voices
            german_voices = [
                v for v in voices_list 
                if v["Locale"].startswith("de-")
            ]
            
            print("\n=== Available German Voices ===")
            for v in german_voices:
                print(f"  {v['ShortName']} - {v['Gender']} ({v['Locale']})")
            
            return german_voices
        
        return asyncio.run(_list())


# ======================================================================== #
#                              TESTING                                     #
# ======================================================================== #

if __name__ == "__main__":
    # Initialize TTS with German voice
    tts = EdgeTTS(voice="de-DE-KatjaNeural")
    
    print("\n=== Testing Edge TTS ===")
    
    # Test sentence
    
    # Test 1
    # -------
    # test_text = "I am testing english and german, Ich bin dein Deutsch-Tutor. Wie kann ich dir heute helfen?"
    # print(f"Speaking: {test_text}")
    # tts.speak(test_text)
    
    # Test 2
    # -------
    test_text = "Guten Morgen! I wanted to check if you finished the report. Hoffentlich geht alles gut bei dir."
    print(f"Speaking: {test_text}")
    tts.speak(test_text)
    
    # Test 3
    # -------
    # test_text = "Hallo! Ich bin dein Deutsch-Tutor. Wie kann ich dir heute helfen?"
    # print(f"Speaking: {test_text}")
    # tts.speak(test_text)
    
    # Test 4
    # -------
    # test_text = "This time I am speaking in English"
    # print(f"Speaking: {test_text}")
    # tts.speak(test_text)
    
    
    # # list all voices
    # EdgeTTS.list_voices()