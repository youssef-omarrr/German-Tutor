import torch
from TTS.api import TTS
import sounddevice as sd

class TextToSpeech:
    def __init__(self, 
                model_name="tts_models/multilingual/multi-dataset/xtts_v2", 
                output_path="output.wav"):
        
        """Initialize the TTS model."""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = model_name
        self.output_path = output_path

        # Load the TTS model
        print(f"Loading model: {self.model_name} on {self.device}...")
        self.tts = TTS(self.model_name).to(self.device)

    def generate(self, text, language="de", speaker_index=0):
        """Generate audio without playing it."""
        return self.tts.tts(
            text=text,
            language=language,
            speaker=self.tts.speakers[speaker_index]
        )

    def play(self, audio, on_start=None):
        """Play pre-generated audio."""
        if on_start:
            on_start()
        sd.play(audio, samplerate=22050)
        sd.wait()

    def synthesize(self, text, language="de", 
                speaker_index=0, 
                on_start=None):
        """
        Convert text to speech and play it (blocking by default).
        
        :param text: The input text to convert.
        :param language: The language code (e.g., 'de', 'en').
        :param speaker_index: Index of the speaker to use.
        :param on_start: Callback function called when audio starts playing.
        """
        import re
        # Naive chunk split on '.' and ':', can be improved with your own splitter
        chunks = [chunk.strip() for chunk in re.split(r'[.:]', text) if chunk.strip()]
        audio_chunks = []
        for chunk in chunks:
            audio = self.generate(chunk, language, speaker_index)
            audio_chunks.append(audio)
            
        # Concatenate audio chunks (assuming numpy arrays)
        import numpy as np
        full_audio = np.concatenate(audio_chunks)
        self.play(full_audio, on_start)


if __name__ == "__main__":
    tts_engine = TextToSpeech()

    sample_text = (
        "Corrected Sentence: "
        "Auf Wiedersehen Explanation: "
        "The phrase  Auf Wieder  is incomplete the usual farewell is Auf Wiedersehen literally  until we see each other again . "
        "German nouns are capitalized, so Wiedersehen starts with a capital W. "
        "Adding an exclamation mark or a period makes the sentence complete and shows the intended tone. "
        "Alternative Wordings slash Style Improvements: "
        "Alternative one: "
        "Bis später Use this informal goodbye when you expect to see the person later the same day. "
        "Alternative two: "
        "Tschüss A casual and friendly way to say  bye  in everyday conversation. "
        "Alternative three: "
        "Bis bald Means  see you soon,  suitable when you plan to meet again sometime in the near future. "
        "Keep up the great work practicing these common farewells will make your German sound natural "
    )
    

    
    tts_engine.synthesize(sample_text, 
                        language="de", 
                        speaker_index=37)