import asyncio
import edge_tts
import playsound
import os


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
        
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir

        # Get the next available numbered output filename
        self.out_path = self._get_next_output_path()

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
        Plays the generated TTS output at the given path.
        If feedback is given, prints it right before playback starts.
        """
        if feedback:
            print(f"[bold yellow]Tutor says:[/] \n{feedback}"
                "\n=================================================================")
        playsound.playsound(audio_path)

    def synthesize(self, text: str):
        """
        Generate and play the TTS audio for the given text.
        """
        asyncio.run(self.generate(text))
        playsound.playsound(self.out_path)


if __name__ == "__main__":
    # Example text for TTS
    sample_text = (
        "Corrected Sentence: "
        "Auf Wiedersehen Explanation: "
        "The phrase Auf Wieder is incomplete; the usual farewell is Auf Wiedersehen, literally until we see each other again. "
        "German nouns are capitalized, so Wiedersehen starts with a capital W. "
        "Adding an exclamation mark or a period makes the sentence complete and shows the intended tone. "
        "Alternative Wordings / Style Improvements: "
        "Alternative one: Bis später — Use this informal goodbye when you expect to see the person later the same day. "
        "Alternative two: Tschüss — A casual and friendly way to say 'bye' in everyday conversation. "
        "Alternative three: Bis bald — Means 'see you soon', suitable when you plan to meet again sometime in the near future. "
        "Keep up the great work; practicing these common farewells will make your German sound natural."
    )

    # Create TTS instance
    tts_engine = TextToSpeech()

    # Generate and play the audio
    tts_engine.synthesize(sample_text)
