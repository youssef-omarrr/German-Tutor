from rich.console import Console

console = Console()

def init_components():
    """Initialize all heavy components and return them."""
    from legos.STT import JarvisSTT
    from legos.LLM import GermanTutor
    from legos.my_TTS import TextToSpeech

    # Create an instance of the speech-to-text listener (JarvisSTT)
    # This object handles detecting the wake word ("Jarvis") and transcribing speech.
    listener = JarvisSTT()
    
    # Create an instance of the German tutor logic
    # This object will handle correcting the user's German sentences and giving feedback.
    tutor = GermanTutor()
    
    # Create an instance of your text-to-speech engine
    tts_engine = TextToSpeech(
        model_name="tts_models/multilingual/multi-dataset/xtts_v2",
        output_path="output.wav"
    )
    return listener, tutor, tts_engine


def run_loop(listener, tutor, tts_engine):
    """
    Main control loop:
        - Wait for "Jarvis" to start a session.
        - While the session is active:
          * Listen for ONE user utterance
          * If it's an end-phrase -> close session
            * Else -> get tutor.correct(...) (returns string)
                    -> print + speak the feedback (blocking)
          * After playback ends, loop back to listen for the next utterance
        - Repeat until global stop (Ctrl+C)
    """

    try:
        # Main loop: keep listening until the program is stopped
        while not listener._stop:
            # 1) Wait for Jarvis to start a session
            listener.console.print("[bold green]Say 'Jarvis' to start a session...[/] (Ctrl+C to exit)")
            started = listener.wait_for_session_start()
            
            if not started:
                break  # stop requested

            # 2) In-session: loop until an end phrase or stop
            while listener.in_session and not listener._stop:
                transcript, is_end = listener.listen_for_user()
                if transcript is None:
                    # nothing detected or timeout — keep listening
                    continue

                # Show recognized text
                listener.console.print(f"\n[bold green]You said:[/] {transcript}")

                # If transcript matched the end phrase, session ends immediately
                if is_end:
                    listener.console.print("[magenta]Session ended by end phrase. Say 'Jarvis' to start again.[/]")
                    listener.in_session = False
                    break

                # 3) Get tutor feedback (method returns the printed string)
                with console.status("[yellow]Loading response...[/]", spinner="weather") as status:
                    feedback, tts_input = tutor.correct(transcript)  # must return string
                    if not feedback or not tts_input.strip():
                        continue
                    
                    # Generate audio while spinner is still showing
                    audio = tts_engine.generate(tts_input, language="de", speaker_index=37)
                    
                    # Stop spinner and set up callback for synchronized print
                    status.stop()
                    
                    # Play audio and print feedback together
                    tts_engine.play(
                        audio,
                        on_start=lambda: listener.console.print(f"[bold yellow]Tutor says:[/] \n{feedback}"
                                                                "\n======================================================================")
                    )
                
            # session ended — loop will go back to waiting for "Jarvis"
    finally:
        listener.console.print("\n[magenta]Exiting... Goodbye![/]")
        listener.cleanup()

if __name__ == "__main__":
    with console.status("[magenta]Loading German Tutor... please wait[/]", spinner="weather"):
        listener, tutor, tts_engine = init_components()  # Spinner runs here

    # Spinner stops here before starting to listen
    run_loop(listener, tutor, tts_engine)
    
    # init at each windows powershell session
    # $Env:HF_TOKEN = "TOKEN"