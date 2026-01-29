"""
Speech-to-Text using Faster-Whisper
Transcribes real-time audio from microphone (not files)
"""

from faster_whisper import WhisperModel
import numpy as np
from typing import Optional, Tuple
from rich.console import Console
from audio_io import AudioRecorder
from end_phrase import EndPhrases


class FasterWhisperSTT:
    """
    Real-time speech-to-text using Faster-Whisper.
    Records from microphone and transcribes.
    """
    
    def __init__(
        self,
        model_size: str = "large-v3",
        device: str = "cuda",  # "cuda" or "cpu"
        compute_type: str = "float16",  # "float16" (GPU) or "int8" (CPU)
        language: str = "de",  # German, None -> for auto language detection mode
        beam_size: int = 5,
        vad_filter: bool = True,  # Voice activity detection
    ):
        """
        Initialize Faster-Whisper model.
        
        Args:
            model_size: Model size (tiny, base, small, medium, large-v3)
                       - tiny: Fastest, least accurate
                       - large-v3: Slowest, most accurate
            device: "cuda" for GPU or "cpu"
            compute_type: "float16" (GPU), "int8" (CPU) for speed
            language: Target language code (de=German, en=English, None -> for auto language detection mode)
            beam_size: Beam search width (higher = better but slower)
            vad_filter: Use voice activity detection to filter silence
        """
        self.console = Console()
        self.language = language
        self.beam_size = beam_size
        self.vad_filter = vad_filter
        
        # Load Faster-Whisper model
        self.console.print(f"[yellow]Loading Faster-Whisper {model_size}...[/]")
        try:
            self.model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
                download_root=None,  # Use default cache
            )
            self.console.print("[green]✓ Model loaded successfully[/]")
        except Exception as e:
            self.console.print(f"[red]Failed to load model: {e}[/]")
            raise
        
        # Initialize audio recorder
        self.recorder = AudioRecorder(
            sample_rate=16000,  # Whisper requires 16kHz
            energy_threshold=200,
            pause_duration=0.5, # <-- this controls how long it waits after silence
            max_duration=10.0,
        )
        
        # Define END PHRASES
        self.end_phrases = EndPhrases()
        
    
    def transcribe(self, audio: np.ndarray) -> Optional[str]:
        """
        Transcribe audio array to text.
        
        Args:
            audio: NumPy array of audio samples (float32, 16kHz)
            
        Returns:
            Transcribed text or None if transcription failed
        """
        try:
            # Transcribe with Faster-Whisper
            segments, info = self.model.transcribe(
                audio,
                language=self.language, # or 'None' to allow auto language detection
                beam_size=self.beam_size,
                vad_filter=self.vad_filter,
                vad_parameters=dict(
                    min_silence_duration_ms=200,  # Minimum silence to split
                    threshold=0.5,  # Voice activity threshold
                ),
            )
            
            # Combine all segments into single transcript
            transcript = " ".join(segment.text for segment in segments).strip()
            
            if not transcript:
                return None
            
            # if auto language detection is on
            # -----------------------------------
            # Log language detection info
            detected_lang = info.language
            lang_probability = info.language_probability
            
            if detected_lang != self.language and lang_probability > 0.5:
                self.console.print(
                    f"[yellow]⚠ Detected {detected_lang} "
                    f"(expected {self.language}, confidence: {lang_probability:.2f})[/]"
                )
            # -----------------------------------------------------------------------------
            
            # Detect end phrase match
            if self.end_phrases.search(transcript):
                self.console.print(f"[italic red]\n⚠  End phrase detected in: {transcript}[/]")
                self.cleanup()
                return "__END_SESSION__"
            
            return transcript
            
        except Exception as e:
            self.console.print(f"[red]Transcription error: {e}[/]")
            return None
    
    def listen_and_transcribe(self) -> Optional[str]:
        """
        Record from microphone and transcribe in one step.
        
        Returns:
            Transcribed text or None if no speech or error
        """
        # Record audio
        audio = self.recorder.record()
        
        if audio is None:
            return None
        
        # Transcribe
        with self.console.status("[bold magenta]Transcribing...[/]", spinner="dots"):
            result = self.transcribe(audio)
            
            if result == "__END_SESSION__":
                return "__END_SESSION__"  # signal caller to exit loop
            
            return result
    
    def cleanup(self):
        """Release resources."""
        self.recorder.cleanup()


# ======================================================================== #
#                              TESTING                                     #
# ======================================================================== #

if __name__ == "__main__":
    # Test with small model for speed
    stt = FasterWhisperSTT(
        # model_size="base",  # Use base for testing (faster)
        device="cpu",  # Change to "cuda" if you have cuad 12 (won't work on cuda 13+)
        compute_type="int8",  # Use int8 for CPU
        language="de"
    )
    
    try:
        print("\n=== Testing Faster-Whisper STT ===")
        print("Speak in German...")
        
        while True:
            transcript = stt.listen_and_transcribe()
            
            if transcript:
                if transcript == "__END_SESSION__":
                    print("\nSession ended")
                    break
                
                print(f"\n✓ You said: {transcript}")
                
            else:
                print("\n✗ No speech detected")
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        stt.cleanup()