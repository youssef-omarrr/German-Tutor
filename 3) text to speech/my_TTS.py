import torch
import threading
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
        print("Available speakers:", self.tts.speakers)
        print("Available languages:", self.tts.languages)

    def synthesize(self, text, language="de", speaker_index=0, async_play=True):
        """
        Convert text to speech and optionally play it.
        
        :param text: The input text to convert.
        :param language: The language code (e.g., 'de', 'en').
        :param speaker_index: Index of the speaker to use.
        :param play: Whether to play the audio after saving.
        """
        def _generate_and_play():
            print(f"[TTS] Synthesizing with {self.tts.speakers[speaker_index]}...")

            # Get audio as a numpy array instead of writing to file
            audio = self.tts.tts(
                text=text,
                language=language,
                speaker=self.tts.speakers[speaker_index]
            )

            # Play it immediately
            sd.play(audio, samplerate=22050)
            sd.wait()  # Wait until playback finishes

        if async_play:
            threading.Thread(target=_generate_and_play, daemon=True).start()
        else:
            _generate_and_play()


if __name__ == "__main__":
    tts_engine = TextToSpeech()

    sample_text = (
        "Hello! Wie geht es dir? "
        "Heute ist ein schöner Tag, and I'm glad we can practice together. "
        "I bought coffee this morning und ein frisches Brötchen. "
        "If you have any questions, frag mich bitte. "
        "Let's try a short exercise now."
    )

    tts_engine.synthesize(sample_text, language="de", 
                        speaker_index=37, 
                        async_play=True)
