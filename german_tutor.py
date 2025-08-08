from legos import JarvisSTT, GermanTutor

# Create an instance of the speech-to-text listener (JarvisSTT)
# This object handles detecting the wake word ("Jarvis") and transcribing speech.
listener = JarvisSTT()

# Create an instance of the German tutor logic
# This object will handle correcting the user's German sentences and giving feedback.
tutor = GermanTutor()

# Print initial prompt for the user in the console
listener.console.print(
    "[bold green]Say 'Jarvis' to start speaking...[/] (Ctrl+C to exit)\n"
)

try:
    # Main loop: keep listening until the program is stopped
    while not listener._stop:
        # Listen once for speech input and convert it to text
        text = listener.listen_once()

        # If no text was returned and the listener was stopped during listening, exit loop
        if text is None and listener._stop:
            break

        # If speech was detected and transcribed
        if text:
            # Show the recognized text in the console
            listener.console.print(f"[bold green]You said:[/] {text}")

            # Pass the recognized text to the German tutor for correction and feedback
            tutor.correct(text)

finally:
    # Runs when the loop ends (e.g., Ctrl+C or program stop)
    # Print exit message and clean up resources (e.g., microphone, threads)
    listener.console.print("\n[magenta]Exiting... Goodbye![/]")
    listener.cleanup()
