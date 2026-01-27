import signal
import speech_recognition as sr
from rich.console import Console
import pvporcupine
import pyaudio
import numpy as np
import re
from typing import Tuple, Optional

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
            timeout: float = 5.0,
            phrase_time_limit: float = 15.0,
        ):
        
        """
        Initialize the wake word engine, audio stream, and recognizer.
        """
        
        # STEP 0: INITIALIZATION
        # --------------------------------
        # Prepare variables, audio devices, and wake word detectors.
        self._stop = False                   # For Ctrl+C stopping
        self.in_session = False               # Whether we’re in an active conversation
        signal.signal(signal.SIGINT, self._handle_sigint)

        self.console = Console()
        self.recognizer = sr.Recognizer()

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
            "bye jarvis",
            "jarvis stop",
            "jarvis fuck off",
            "auf wiedersehen jarvis",
            "tschüss jarvis",
            "bye bye",
            "goodbye",
            "tschüss",
            "close"
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
        return False
    
    # ---------------------------------------------------------------- #
    def wait_for_session_start(self) -> bool:
        """
        Public method: wait for 'Jarvis' and enter session mode.
        Returns True if session started, False if stop requested.
        """
        if self._wait_for_wakeword():
            self.in_session = True
            self.console.print("[cyan]Session started![/] Speak freely, say 'Bye Jarvis' to end.")
            return True
        return False
    
    # -------------------------------------------------------------------- #
    
    def _listen_for_speech(self) -> str | None:
        """
        STEP 2: LISTEN (SPEECH RECOGNITION)
        - Uses speech_recognition's Microphone + Google STT to get a transcript.
        - We do this only during the active session.
        """
        with sr.Microphone() as source, self.console.status("[bold blue]Speak now...[/]", spinner="earth"):
            # Reduce background noise impact
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                # Wait for speech, then record until pause or time limit
                audio = self.recognizer.listen(
                    source,
                    timeout=self.timeout,
                    phrase_time_limit=self.phrase_time_limit
                )
            except Exception:
                return None

        # Try to recognize using Google STT
        try:
            return self.recognizer.recognize_google(audio, language=self.language)
        except (sr.UnknownValueError, sr.RequestError):
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

        # Detect explicit end phrases (case-insensitive, whole phrase match)
        if self._end_re.search(transcript):
            # Print the detected phrase
            self.console.print(f"[italic red]End phrase detected in: {transcript}[/]")
            # mark session as finished
            self.in_session = False
            return transcript, True

        return transcript, False

    # -------------------------------------------------------------------- #

    def cleanup(self):
        """
        STEP 4: CLEANUP - Release all audio and wake word resources.
        """
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
        listener.listen_loop()
    finally:
        listener.console.print("\n[magenta]Exiting... Goodbye![/]")
        listener.cleanup()
