"""
Wake Word Detection using Porcupine
Detects "Jarvis" to start sessions
"""

import pvporcupine 
import pyaudio
import numpy as np
from rich.console import Console
import time
import signal

from dotenv import load_dotenv
import os

# load .env file tp get access keys
load_dotenv()

class WakeWordDetector:
    """
    Listens for wake word ('Jarvis') using Porcupine.
    """
    def __init__(self,
                keyword: str = "jarvis",
                sensitivity: float = 0.9):
        """
        Initialize Porcupine wake word detector.
        
        Args:
            keyword: Wake word to detect (default: "jarvis"), other options:
                - "terminator"
                - "hey_siri"
                - "computer"
                - "porcupine"
            sensitivity: Detection sensitivity 0.0-1.0 (higher = more sensitive)
        """
        
        # init console
        self.console = Console()
        
        # init porcupine
        self.keyword = keyword
        self.porcupine = pvporcupine.create(
            access_key = os.getenv("PORCUPINE_ACCESS_KEY"),
            keywords = [keyword],
            sensitivities = [sensitivity],
        )
        
        # setup pyaudio stream for wake work detection
        # NOTE: we only use this stream for the start hotword
        self._pa = pyaudio.PyAudio()
        self.stream = self._pa.open(
            rate = self.porcupine.sample_rate,
            channels = 1,
            format = pyaudio.paInt16,
            input = True,
            frames_per_buffer = self.porcupine.frame_length,
        )
        
    # ---------------------------------------------------------------- #
    def wait_for_wake_word(self):
        """
        Wait for wake word to be spoken.
        
        Returns:
            True if wake word detected, False if stopped
        """
        with self.console.status(
            f"[bold cyan]Waiting for '{self.keyword}'...[/]", 
            spinner="moon"
        ):
            try:
                while True:
                    # Read audio frame
                    pcm_bytes = self.stream.read(
                        self.porcupine.frame_length,
                        exception_on_overflow=False
                    )
                    
                    # Convert to numpy array
                    pcm = np.frombuffer(pcm_bytes, dtype=np.int16)
                    
                    # Check for wake word
                    result = self.porcupine.process(pcm)
                    if result >= 0:
                        self.console.print(f"[green]✓ '{self.keyword}' detected!, Starting session...[/]")
                        return True
            
            # NOTE: WILL BE REMOVED AND ADDED TO audio_io.py
            # For Ctrl+C stopping
            except KeyboardInterrupt: 
                self.console.print("[red]Exiting...[/]")
                return False

    # ---------------------------------------------------------------- #
    def cleanup(self):
        """Release resources."""
        try:
            self.stream.stop_stream()
            self.stream.close()
        except:
            pass
        
        try:
            self._pa.terminate()
        except:
            pass
        
        try:
            self.porcupine.delete()
        except:
            pass
        
        
# ======================================================================== #
#                              TESTING                                     #
# ======================================================================== #

if __name__ == "__main__":
    detector = WakeWordDetector()
    try:
        while True:
            if detector.wait_for_wake_word():
                print("Wake word detected! Starting session...")
                time.sleep(2)  # Simulate session
    finally:
        detector.cleanup()