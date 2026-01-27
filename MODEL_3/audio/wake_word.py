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

class WakeWordDetector:
    """
    Listens for wake word ('Jarvis') using Porcupine.
    """
    def __init__(self,
                keyword: str = "jatvis",
                sensitivity: float = 0.9):
        """
        Initialize Porcupine wake word detector.
        
        Args:
            keyword: Wake word to detect (default: "jarvis")
            sensitivity: Detection sensitivity 0.0-1.0 (higher = more sensitive)
        """
        
        # init console
        self.console = Console()
        
        # init porcupine
        self.keyword = keyword
        self.porcupine = pvporcupine.create(
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
            frames_per_buffer = self.porcupine.frame_length,
        )
        
        # For Ctrl+C stopping
        self.stop = False
        signal.signal(signal.SIGINT, self._handle_sigint)
        
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
            while not self.stop:
                try:
                    # Read audio frame
                    pcm_bytes = self._stream.read(
                        self.porcupine.frame_length,
                        exception_on_overflow=False
                    )
                    
                    # Convert to numpy array
                    pcm = np.frombuffer(pcm_bytes, dtype=np.int16)
                    
                    # Check for wake word
                    result = self.porcupine.process(pcm)
                    if result >= 0:
                        self.console.print(f"[green]✓ '{self.keyword}' detected![/]")
                        return True
                        
                except Exception as e:
                    # Handle audio errors gracefully
                    time.sleep(0.05)
                    continue
                    
        return False
    
    # ---------------------------------------------------------------- #
    def _handle_sigint(self, sig, frame):
        """
        Signal handler to safely stop the loop on Ctrl+C.
        """
        self._stop = True

    # ---------------------------------------------------------------- #
    def cleanup(self):
        """Release resources."""
        try:
            self._stream.stop_stream()
            self._stream.close()
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
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        detector.cleanup()