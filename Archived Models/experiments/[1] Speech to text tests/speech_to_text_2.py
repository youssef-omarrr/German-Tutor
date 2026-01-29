import signal
import speech_recognition as sr
from rich.console import Console
import pvporcupine
import pyaudio
import numpy as np

# Create a single Rich Console instance for rendering
console = Console()

# ======================================================================== #

def listen_real_time():
    """
    Continuously listen to German speech from the microphone.
    Waits for 'Jarvis' hotword before starting each listening session.
    Displays a Rich spinner with "Speak now..." while listening.
    Transcribes speech and prints the results.
    Handles Ctrl+C gracefully to stop the loop.
    """
    
    # ======================================================================== #
    # This is a flag that will be used to control the main loop (init to false to keep main running)
    stop_main = False

    # Custom signal handler to catch Ctrl+C
    def handle_sigint(sig, frame):
        # "nonlocal" allows the handler to modify the stop_main variable
        nonlocal stop_main
        stop_main = True

    '''
    This tells Python to use your "handle_sigint" function instead of the default behavior 
    (which raises a KeyboardInterrupt exception) when Ctrl+C is pressed.
    '''
    signal.signal(signal.SIGINT, handle_sigint)
    # ======================================================================== #
    
    # init recognizer
    recognizer = sr.Recognizer()
    
    # === Porcupine setup ===
    porcupine = pvporcupine.create(
                        keywords=["jarvis"], # Wake up keyword
                        sensitivities=[0.8]  # sensitivity
                        )
    
    # init PyAudio to capture raw microphone input
    pa = pyaudio.PyAudio()
    
    # Open a single-channel audio stream with parameters matching Porcupine
    audio_stream = pa.open(
        rate=porcupine.sample_rate,        # Sample rate required by Porcupine
        channels=1,                        # Mono audio
        format=pyaudio.paInt16,           # 16-bit signed PCM
        input=True,                       # This stream is an input (microphone)
        frames_per_buffer=porcupine.frame_length  # Frame length expected by Porcupine
    )
    
    # ======================================================================== #
    
    with sr.Microphone() as source:
        
        # 0) Calibrate mic to ambient noise for accuracy
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        console.print("[bold green]Say 'Jarvis' to start speaking...[/] (press Ctrl+C to exit)\n")

        while not stop_main:
            
            # 1) Wait for wake word
            with console.status("[bold cyan]Say 'Jarvis' to begin...[/]", spinner="moon"):
                while True:
                    # Read a single frame of raw audio data from the microphone
                    pcm_bytes = audio_stream.read(
                                porcupine.frame_length,  # Number of samples per frame as expected by Porcupine
                                exception_on_overflow=False # Prevent exception if buffer overflows—just drop old data
                                )
                    
                    # Quickly convert the raw byte buffer into an array of 16-bit signed integers
                    pcm = np.frombuffer(pcm_bytes,   # Byte buffer returned by PyAudio
                                        dtype=np.int16 # Data type matching pyaudio.paInt16 format
                                        )
                    
                    # Process the audio frame through Porcupine
                    # - Returns an index ≥ 0 when the wake word ("jarvis") is detected
                    # - We also exit early if stop_main has been set by Ctrl+C handler
                    if porcupine.process(pcm) >= 0 or stop_main:
                        break

            if stop_main:
                break
            
            # ======================================================================== #
            # 2) Wake word detected-> record the phrase
            with console.status("[bold blue]Speak now...[/]", spinner="earth"):
                try:
                    audio = recognizer.listen(source,
                                            timeout=5, # the max number of seconds that this will wait for a phrase to start before giving up.
                                            phrase_time_limit=15 # the max number of seconds that this will allow a phrase to continue before stopping 
                                                                # and returning the part of the phrase processed before the time limit was reached.
                                            ) 
                except Exception as e:
                    console.log(f"[bold red]Error listening:[/] {e}")
                    continue

            # ======================================================================== #
            # 3) Transcribe recorded audio
            try:
                text = recognizer.recognize_google(audio, language="de-DE")
                console.print(f"[bold green]You said:[/] {text}")
                
            except sr.UnknownValueError:
                console.print("[yellow]Sorry, didn't catch that.[/]")
            except sr.RequestError as e:
                console.print(f"[bold red]API error:[/] {e}")

        console.print("\n[bold magenta]Exiting... Goodbye![/]")
        
        
    # Clean up Porcupine and PyAudio
    audio_stream.stop_stream()
    audio_stream.close()
    porcupine.delete()
    pa.terminate()

# ======================================================================== #
# ===========================  MAIN   ==================================== #
# ======================================================================== #

if __name__ == "__main__":
    listen_real_time()
