import signal
import speech_recognition as sr
from rich.console import Console
import pvporcupine
import pyaudio
import numpy as np
import re
from typing import Tuple, Optional
import time
from threading import Lock
from rapidfuzz import fuzz


# ======================================================================== #
#                            JARVIS SPEECH-TO-TEXT                         #
# ======================================================================== #

class JarvisSTT:
    """
    Wait for 'Jarvis' (Porcupine). Once session started, repeatedly:
        - listen for 1 user utterance (speech_recognition)
        - return transcript + whether it matched an end phrase
    """

    def __init__(
            self,
            language: str = "de-DE",
            sensitivity: float = 0.8,
            timeout: float = 3.0,  # Reduced from 60s - this was causing the slow response!
            phrase_time_limit: float = 10.0,  # Reduced from 15s for faster cutoff
        ):
        
        """
        Initialize the wake word engine, audio stream, and recognizer.
        """
        
        # STEP 0: INITIALIZATION
        # --------------------------------
        # Prepare variables, audio devices, and wake word detectors.
        self._stop = False                   # For Ctrl+C stopping
        self.in_session = False               # Whether we're in an active conversation
        signal.signal(signal.SIGINT, self._handle_sigint)

        self.console = Console()
        self.recognizer = sr.Recognizer()
        
        # Aggressive optimization for faster response times
        # These settings prioritize speed over perfect noise handling
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.energy_threshold = 200  # Even lower for faster detection
        self.recognizer.pause_threshold = 0.5   # Shorter pause = faster response
        self.recognizer.phrase_threshold = 0.3  # Faster phrase detection
        self.recognizer.non_speaking_duration = 0.3  # Quick silence detection
        
        # Session state tracking for better resource management
        self._session_lock = Lock()
        self._calibrated = False

        # Porcupine only for "jarvis" (session start)
        self.porcupine_jarvis = pvporcupine.create(
            keywords=["jarvis"],
            sensitivities=[sensitivity],
        )

        # Open pyaudio stream for Porcupine wake-word detection
        # NOTE: we only use this stream for the start hotword; during actual speech capture
        # we use speech_recognition's Microphone which opens its own stream.
        self._pa = pyaudio.PyAudio()
        self._stream = self._pa.open(
            rate=self.porcupine_jarvis.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine_jarvis.frame_length,
        )

        # Language and timing parameters for recognition
        self.language = language
        self.timeout = timeout
        self.phrase_time_limit = phrase_time_limit

        # ====================================== #
        
        # End phrases to check for in the transcript to end the session.
        self.end_phrases = [
            "bye",
            "stop",
            "fuck off",
            "auf wiedersehen",
            "tschüss",
            "bye bye",
            "goodbye",
            "close",
            "okay bye",
            "that's all, thanks",
            "we're done",
            "bye jarvis",
            "stop jarvis"
        ]
        # Build a regex that matches any end phrase as a whole word/phrase
        # This reduces false positives like "I bought a new computer" (still possible, so prefer specific phrases).
        joined = "|".join(re.escape(p) for p in self.end_phrases)
        self._end_re = re.compile(rf"\b({joined})\b", flags=re.IGNORECASE)

    # -------------------------------------------------------------------- #

    def _handle_sigint(self, sig, frame):
        """
        Signal handler to safely stop the loop on Ctrl+C.
        """
        self._stop = True

    # -------------------------------------------------------------------- #
    
    def _wait_for_wakeword(self) -> bool:
        """
        STEP 1: WAIT FOR WAKEWORD ("jarvis")
        - Use Porcupine and our pyaudio stream to detect the start-hotword.
        - Returns True if detected, False if we're stopping.
        """
        with self.console.status("[bold cyan]Waiting for 'Jarvis'...[/]", spinner="moon"):
            while not self._stop:
                try:
                    # Read audio frame from microphone
                    pcm_bytes = self._stream.read(
                        self.porcupine_jarvis.frame_length,
                        exception_on_overflow=False
                    )
                    # Convert raw bytes → numpy array for Porcupine
                    pcm = np.frombuffer(pcm_bytes, dtype=np.int16)
                    # Check if wake word was spoken
                    if self.porcupine_jarvis.process(pcm) >= 0:
                        return True
                except Exception:
                    # Simple error handling without console spam
                    time.sleep(0.05)  # Reduced sleep time for faster recovery
                    continue
        return False
    
    # ---------------------------------------------------------------- #
    def wait_for_session_start(self) -> bool:
        """
        Public method: wait for 'Jarvis' and enter session mode.
        Returns True if session started, False if stop requested.
        """
        if self._wait_for_wakeword():
            with self._session_lock:
                self.in_session = True
                
                # Fast calibration strategy: pre-initialize microphone source
                # This eliminates device opening delays during the session
                if not self._calibrated:
                    try:
                        # Quick calibration with fresh microphone instance
                        with sr.Microphone() as source:
                            # Ultra-fast calibration - just enough to set baseline
                            self.recognizer.adjust_for_ambient_noise(source, duration=0.1)
                            self._calibrated = True
                    except Exception:
                        # Fallback: use default settings
                        pass
                
            self.console.print("[cyan]Session started![/] Speak freely, say 'Bye Jarvis' to end.")
            return True
        return False
    
    # -------------------------------------------------------------------- #
    
    def _listen_for_speech(self) -> str | None:
        """
        STEP 2: LISTEN (SPEECH RECOGNITION)
        - Uses speech_recognition's Microphone + Google STT to get a transcript.
        - We do this only during the active session.
        - Optimized to avoid repeated calibration and reduce latency
        """
        try:
            # Always use fresh microphone instance to avoid device conflicts
            # The persistent source was causing the infinite loop issue
            with sr.Microphone() as source, self.console.status("[bold blue]Speak now...[/]", spinner="earth"):
                # Skip ambient noise adjustment during session - we calibrated once at session start
                # This significantly speeds up response time between utterances
                try:
                    # Wait for speech, then record until pause or time limit
                    audio = self.recognizer.listen(
                        source,
                        timeout=self.timeout,
                        phrase_time_limit=self.phrase_time_limit
                    )
                except sr.WaitTimeoutError:
                    # Timeout is normal - user might not be speaking
                    return None
                except Exception:
                    return None

            # Try to recognize using Google STT
            try:
                return self.recognizer.recognize_google(audio, language=self.language)
            except (sr.UnknownValueError, sr.RequestError):
                return None
                
        except Exception:
            # Device busy or other error - return None without console spam
            return None
    
    # -------------------------------------------------------------------- #

    def listen_for_user(self) -> Tuple[Optional[str], bool]:
        """
        Public: listen once for the user's utterance while in-session.

        Returns:
            (transcript_or_None, is_end_phrase)
        - transcript_or_None: recognized string or None
        - is_end_phrase: True if transcript matched an end phrase (session should end)
        """
        transcript = self._listen_for_speech()
        if transcript is None:
            return None, False

        # 1) Exact or regex end phrase match
        if self._end_re.search(transcript):
            self.console.print(f"[italic red]\n⚠  End phrase detected in: {transcript}[/]")
            with self._session_lock:
                self.in_session = False
                self._calibrated = False
            return transcript, True

        # 2) Fuzzy match check for each end phrase
        for phrase in self.end_phrases:
            similarity = fuzz.ratio(transcript.lower(), phrase.lower())
            if similarity >= 85:  # Threshold can be adjusted
                self.console.print(f"[italic red]\n⚠  Fuzzy end phrase match (({round(similarity, 2)})%): {transcript}[/]")
                with self._session_lock:
                    self.in_session = False
                    self._calibrated = False
                return transcript, True

        return transcript, False

    # -------------------------------------------------------------------- #
    
    def listen_loop(self):
        """
        Main execution loop: wait for wake word, then handle session until end phrase.
        Optimized session management with minimal console output.
        """
        try:
            while not self._stop:
                # Wait for session to start
                if not self.wait_for_session_start():
                    break
                
                # Active session loop - streamlined for performance
                while self.in_session and not self._stop:
                    transcript, is_end = self.listen_for_user()
                    
                    if transcript:
                        if is_end:
                            # Clean session end without extra output
                            break
                        else:
                            # Return transcript for processing by caller
                            # No automatic console printing to keep output clean
                            yield transcript
                    # Continue listening if no speech detected (transcript is None)
                        
        except KeyboardInterrupt:
            pass  # Clean exit on Ctrl+C
        except Exception:
            pass  # Silent error handling to avoid console spam

    def cleanup(self):
        """
        STEP 4: CLEANUP - Release all audio and wake word resources.
        """
        # Clean up persistent microphone source
        try:
            self._stream.stop_stream()
            self._stream.close()
        except Exception:
            pass
        try:
            self.porcupine_jarvis.delete()
        except Exception:
            pass
        try:
            self._pa.terminate()
        except Exception:
            pass

# ======================================================================== #
#                                ENTRY POINT                               #
# ======================================================================== #

if __name__ == "__main__":
    listener = JarvisSTT()
    try:
        # Example usage with clean output handling
        for transcript in listener.listen_loop():
            # Process transcript here - only print when you want to
            print(f"User said: {transcript}")
    finally:
        listener.console.print("\n[magenta]Exiting... Goodbye![/]")
        listener.cleanup()