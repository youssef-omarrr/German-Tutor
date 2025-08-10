import asyncio
import edge_tts
from rich.console import Console
import os
import warnings
from threading import Event
from pynput import keyboard

# Suppress Pygame greeting
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

# Suppress pkg_resources deprecation warning
warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")

from pygame import mixer  # Import AFTER setting env + warnings


class TextToSpeech:
    """
    Text-to-Speech wrapper using edge_tts (Azure Neural voices).
    
    Main methods:
    - generate(text): Asynchronously synthesize speech and save it to an MP3 file.
    - synthesize(text): Generate speech and play it immediately.
    
    Features:
    - Saves each output file in 'output_audio/' with incrementing numbers:
    output_1.mp3, output_2.mp3, etc.
    """

    def __init__(self, language: str = "de",
                voice: str = "de-DE-KatjaNeural",
                output_dir: str = "output_audio",
                rate: str = "+10%"):
        
        # TTS voice settings
        self.language = language
        self.voice = voice
        self.rate = rate
        
        self.console = Console()
        
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir

        # Get the next available numbered output filename
        self.out_path = self._get_next_output_path()
        
        # Event listener to stop audio
        self.stop_event = Event()


    def _get_next_output_path(self) -> str:
        """
        Find the next available output filename in sequence.
        Example: output_1.mp3, output_2.mp3, ...
        """
        existing_files = [
            f for f in os.listdir(self.output_dir)
            if f.startswith("output_") and f.endswith(".mp3")
        ]
        numbers = []
        for f in existing_files:
            try:
                num = int(f[len("output_"):-4])
                numbers.append(num)
            except ValueError:
                pass
        next_number = max(numbers, default=0) + 1
        return os.path.join(self.output_dir, f"output_{next_number}.mp3")

    async def generate(self, text: str):
        """
        Asynchronously generate the TTS output and save to self.out_path.
        Returns the file path of the generated audio.
        
        and returns that path
        """
        tts = edge_tts.Communicate(
            text=text,
            voice=self.voice,
            rate=self.rate
        )
        await tts.save(self.out_path)
        return self.out_path
    
    def play (self, 
            audio_path: str, 
            feedback: str = None
            ):
        """
        Plays the generated TTS output at the given path, allowing stop via Shift+C.
        If feedback is given, prints it right before playback starts.
        """
        
        # 1. if feedback is given
        if feedback:
            self.console.print(f"[bold yellow]Tutor says...[/] (Shift+C to Stop audio) \n{feedback}"
                "\n=================================================================")
        
        # 2. init mixer and clear the stop_playing flag
        mixer.init()
        self.stop_event.clear()
        
        # 3. handling playing the audio
        mixer.music.load(audio_path)
        mixer.music.play()

        # 4. Start hotkey listener in background
        listener = keyboard.GlobalHotKeys({
            '<shift>+c': self.stop
        })
        listener.start()

        # 5. Keep looping until audio finishes or stop requested
        while mixer.music.get_busy() and not self.stop_event.is_set():
            pass

        mixer.music.stop()
        mixer.quit()
        listener.stop()

    def stop(self):
        """
        Stop audio playback immediately.
        """
        """Stop playback."""
        self.stop_event.set()
        mixer.music.stop()
        self.console.print("[red]Audio stopped.[/]")
        
        
    def synthesize(self, text: str):
        """
        Generate and play the TTS audio for the given text.
        """
        self.play( asyncio.run(self.generate(text)) )


if __name__ == "__main__":
    # Example text for TTS
    # sample_text = (
    #     "Corrected Sentence: "
    #     "Auf Wiedersehen Explanation: "
    #     "The phrase Auf Wieder is incomplete; the usual farewell is Auf Wiedersehen, literally until we see each other again. "
    #     "German nouns are capitalized, so Wiedersehen starts with a capital W. "
    #     "Adding an exclamation mark or a period makes the sentence complete and shows the intended tone. "
    #     "Alternative Wordings / Style Improvements: "
    #     "Alternative one: Bis später — Use this informal goodbye when you expect to see the person later the same day. "
    #     "Alternative two: Tschüss — A casual and friendly way to say 'bye' in everyday conversation. "
    #     "Alternative three: Bis bald — Means 'see you soon', suitable when you plan to meet again sometime in the near future. "
    #     "Keep up the great work; practicing these common farewells will make your German sound natural."
    # )
    
    sample_text = ("Good day sir, call my name whenever you need my assistance")

    # Create TTS instance
    tts_engine = TextToSpeech(output_dir= "replies/")

    # Generate and play the audio
    tts_engine.synthesize(sample_text)
