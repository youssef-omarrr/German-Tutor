"""
Text-to-Speech using Edge-TTS
Fast, free, high-quality German voices
"""

import edge_tts
import asyncio
import threading
import sys
from typing import Optional
from rich.console import Console
import tempfile
import os
import subprocess

# Fix SSL/ProactorEventLoop errors on Windows (Python 3.10)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


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
        self._process: Optional[subprocess.Popen] = None
        self._speak_thread: Optional[threading.Thread] = None
    
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
        self._process = process
        stream = communicate.stream()

        try:
            async for chunk in stream:
                if chunk["type"] == "audio":
                    if process.poll() is not None:
                        break  # process was killed, stop streaming
                    try:
                        process.stdin.write(chunk["data"])
                    except BrokenPipeError:
                        break  # mpv was terminated, stop quietly
        finally:
            await stream.aclose()  # cleanly close aiohttp connection
            if process.stdin:
                try:
                    process.stdin.close()
                except Exception:
                    pass
            process.wait()
            self._process = None

    def stop(self):
        """Interrupt TTS playback immediately."""
        if self._process and self._process.poll() is None:
            self._process.terminate()
            self._process = None

    def speak(self, text: str):
        """
        Synthesize and play audio immediately.
        Tries direct streaming with mpv first, falls back to temp file method.
        """
        if not text:
            return
        
        with self.console.status("[bold green]🔊 Speaking...[/]", spinner="material"):
            # First try direct streaming with mpv
            try:
                asyncio.run(self._stream_speak(text))
                return  # Success, exit function
            except Exception as e:
                self.console.print(f"[yellow]Streaming failed: {e}. Falling back to temp file method...[/]")
            
            # Fallback: synthesize to bytes, write temp file, play with mpv
            try:
                audio_data = asyncio.run(self._synthesize(text))
                if not audio_data:
                    self.console.print("[red]TTS synthesis returned no audio.[/]")
                    return

                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                    tmp.write(audio_data)
                    tmp_path = tmp.name

                subprocess.run(["mpv", "--no-terminal", tmp_path], check=True)
                os.unlink(tmp_path)
            except Exception as e:
                self.console.print(f"[red]Playback error: {e}[/]")
    
    # ======================================== #
    #    [OPTIONAL] PLAY FROM TEMP FILE        #
    # ======================================== #
    async def _synthesize(self, text: str) -> Optional[bytes]:
        """
        Synthesize text to audio bytes (async).
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio data as bytes (MP3 format)
        """
        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=self.voice,
                rate=self.rate,
                pitch=self.pitch
            )
            
            # Collect audio chunks
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            return audio_data if audio_data else None
            
        except Exception as e:
            self.console.print(f"[red]TTS synthesis error: {e}[/]")
            return None
    
    def synthesize(self, text: str) -> Optional[bytes]:
        """
        Synthesize text to audio (synchronous wrapper).
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio data as bytes (MP3 format)
        """
        return asyncio.run(self._synthesize(text))
    
    # ======================================== #
    #    [OPTIONAL] VOICES LISTING FUNCTION    #
    # ======================================== #
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