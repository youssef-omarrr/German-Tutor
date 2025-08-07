import signal
import speech_recognition as sr
from rich.console import Console
import pvporcupine
import pyaudio
import numpy as np

# ======================================================================== #
#                            JARVIS SPEECH-TO-TEXT                         #
# ======================================================================== #

class JarvisSTT:
    """
    A class that activates on a wake word ('Jarvis') and transcribes
    a single spoken phrase using Google's Speech Recognition API.
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
        # Flag for stopping the loop gracefully
        self._stop = False
        signal.signal(signal.SIGINT, self._handle_sigint)  # Capture Ctrl+C

        # ====================================== #
        
        # Rich console for status messages
        self.console = Console()

        # Initialize the speech recognizer
        self.recognizer = sr.Recognizer()

        # ====================================== #
        
        # Create the Porcupine wake word detector
        self.porcupine = pvporcupine.create(
            keywords=["jarvis"],
            sensitivities=[sensitivity],
        )

        # Set up PyAudio stream for the wake word engine
        self._pa = pyaudio.PyAudio()
        self._stream = self._pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length,
        )

        # ====================================== #
        
        # Language and timing parameters for recognition
        self.language = language
        self.timeout = timeout
        self.phrase_time_limit = phrase_time_limit

    # -------------------------------------------------------------------- #

    def _handle_sigint(self, sig, frame):
        """
        Signal handler to safely stop the loop on Ctrl+C.
        """
        self._stop = True

    # -------------------------------------------------------------------- #

    def listen_once(self) -> str | None:
        """
        Waits for the wake word, then captures a phrase and returns its transcription.

        Returns:
            str | None: Transcribed text if successful, else None.
        """

        # 1) Wait for the keyword to be detected
        with self.console.status(f"[bold cyan]Waiting for 'Jarvis'...[/]", spinner="moon"):
            while not self._stop:
                # Read audio stream in chunks required by Porcupine
                pcm_bytes = self._stream.read(
                            self.porcupine.frame_length,  # Number of samples per frame as expected by Porcupine
                            exception_on_overflow=False # Prevent exception if buffer overflows—just drop old data
                            )
                
                # Quickly convert the raw byte buffer into an array of 16-bit signed integers
                pcm = np.frombuffer(pcm_bytes,   # Byte buffer returned by PyAudio
                                    dtype=np.int16 # Data type matching pyaudio.paInt16 format
                                    )
                
                # Process the audio frame through Porcupine
                # - Returns an index ≥ 0 when the wake word ("jarvis") is detected
                # - We also exit early if stop_main has been set by Ctrl+C handler
                if self.porcupine.process(pcm) >= 0:
                    break # Wake word detected

        # If stopped via signal, exit early
        if self._stop:
            return None

        # ====================================== #
        # 2) Capture audio after wake word is detected
        with sr.Microphone() as source, \
            self.console.status("[bold blue]Speak now...[/]", spinner="earth"):

            # Calibrate for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

            try:
                # Listen with timeout and max phrase time
                audio = self.recognizer.listen(
                    source,
                    timeout=self.timeout, # the max number of seconds that this will wait for a phrase to start before giving up.
                    phrase_time_limit=self.phrase_time_limit # the max number of seconds that this will allow a phrase to continue before stopping 
                                        # and returning the part of the phrase processed before the time limit was reached.
                ) 
            except Exception:
                return None  # Timed out or interrupted

        # ====================================== #
        # 3) Attempt to transcribe the captured audio
        try:
            return self.recognizer.recognize_google(audio, language=self.language)
        except (sr.UnknownValueError, sr.RequestError):
            return None  # Speech not recognized or API error

    # -------------------------------------------------------------------- #

    def cleanup(self):
        """
        Release audio and wake word engine resources.
        """
        self._stream.stop_stream()
        self._stream.close()
        self.porcupine.delete()
        self._pa.terminate()

# ======================================================================== #
#                                ENTRY POINT                               #
# ======================================================================== #

if __name__ == "__main__":
    # Create instance of the voice listener
    listener = JarvisSTT()

    # Prompt user
    listener.console.print(
        "[bold green]Say 'Jarvis' to start speaking...[/] (Ctrl+C to exit)\n"
    )

    try:
        # Continuously listen for input until stopped
        while not listener._stop:
            text = listener.listen_once()

            # Exit if stopped during listen
            if text is None and listener._stop:
                break

            # If something was said and recognized
            if text:
                listener.console.print(f"[bold green]You said:[/] {text}")

    finally:
        # Graceful exit
        listener.console.print("\n[magenta]Exiting... Goodbye![/]")
        listener.cleanup()
