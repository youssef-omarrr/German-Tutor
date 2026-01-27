"""
Audio I/O utilities for recording and playback
Real-time microphone recording with silence detection
"""

import pyaudio
import numpy as np
from typing import Optional
from rich.console import Console


class AudioRecorder:
    """
    Records audio from microphone with silence detection.
    Real-time recording, not file-based.
    """
    
    def __init__(
        self,
        sample_rate: int = 16000,  # Whisper expects 16kHz
        channels: int = 1,
        chunk_size: int = 1024,
        energy_threshold: int = 200,  # Audio energy to detect speech
        pause_duration: float = 1.0,  # Seconds of silence to stop
        max_duration: float = 10.0,  # Max recording length
    ):
        """
        Initialize audio recorder.
        
        Args:
            sample_rate: Sample rate in Hz (16000 for Whisper)
            channels: Number of audio channels (1 = mono)
            chunk_size: Audio buffer size
            energy_threshold: Minimum energy to detect speech
            pause_duration: Silence duration before stopping
            max_duration: Maximum recording time in seconds
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.energy_threshold = energy_threshold
        self.pause_duration = pause_duration
        self.max_duration = max_duration
        
        self.console = Console()
        self._pa = pyaudio.PyAudio()
    
    def record(self) -> Optional[np.ndarray]:
        """
        Record audio from microphone until silence detected.
        
        Returns:
            NumPy array of audio samples (float32, normalized to [-1, 1])
            or None if no speech detected
        """
        try:
            # Open microphone stream
            stream = self._pa.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            frames = []
            silent_chunks = 0
            recording_started = False
            
            # Calculate max chunks based on durations
            max_silent_chunks = int(
                self.pause_duration * self.sample_rate / self.chunk_size
            )
            max_total_chunks = int(
                self.max_duration * self.sample_rate / self.chunk_size
            )
            
            with self.console.status("[bold blue]🎤 Listening...[/]", spinner="dots"):
                for chunk_num in range(max_total_chunks):
                    # Read audio chunk
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    frames.append(data)
                    
                    # Calculate audio energy (amplitude)
                    audio_chunk = np.frombuffer(data, dtype=np.int16)
                    energy = np.abs(audio_chunk).mean()
                    
                    # Detect speech vs silence
                    if energy > self.energy_threshold:
                        recording_started = True
                        silent_chunks = 0
                    elif recording_started:
                        silent_chunks += 1
                        
                        # Stop if enough silence after speech
                        if silent_chunks > max_silent_chunks:
                            break
            
            # Cleanup stream
            stream.stop_stream()
            stream.close()
            
            # Return None if no speech detected
            if not recording_started:
                return None
            
            # Convert frames to numpy array
            audio_data = b''.join(frames)
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            
            # Normalize to float32 in range [-1, 1] (required by Whisper)
            audio_float = audio_np.astype(np.float32) / 32768.0
            
            return audio_float
            
        except Exception as e:
            self.console.print(f"[red]Recording error: {e}[/]")
            return None
    
    def cleanup(self):
        """Release PyAudio resources."""
        try:
            self._pa.terminate()
        except:
            pass


class AudioPlayer:
    """
    Plays audio through speakers.
    """
    
    def __init__(self, sample_rate: int = 22050):
        """
        Initialize audio player.
        
        Args:
            sample_rate: Playback sample rate
        """
        self.sample_rate = sample_rate
        self._pa = pyaudio.PyAudio()
    
    def play(self, audio: np.ndarray, sample_rate: Optional[int] = None):
        """
        Play audio array through speakers.
        
        Args:
            audio: Audio samples as numpy array
            sample_rate: Override default sample rate
        """
        if sample_rate is None:
            sample_rate = self.sample_rate
        
        try:
            # Convert to int16 if needed
            if audio.dtype == np.float32 or audio.dtype == np.float64:
                audio = (audio * 32767).astype(np.int16)
            
            # Open playback stream
            stream = self._pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                output=True
            )
            
            # Play audio
            stream.write(audio.tobytes())
            
            # Cleanup
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            print(f"Playback error: {e}")
    
    def cleanup(self):
        """Release PyAudio resources."""
        try:
            self._pa.terminate()
        except:
            pass


# ======================================================================== #
#                              TESTING                                     #
# ======================================================================== #

if __name__ == "__main__":
    print("Testing audio recording...")
    recorder = AudioRecorder(energy_threshold=200, pause_duration=1.5)
    
    try:
        print("Speak now...")
        audio = recorder.record()
        
        if audio is not None:
            print(f"Recorded {len(audio)} samples ({len(audio)/16000:.2f} seconds)")
            print(f"Audio shape: {audio.shape}")
            print(f"Audio dtype: {audio.dtype}")
            print(f"Audio range: [{audio.min():.3f}, {audio.max():.3f}]")
        else:
            print("No speech detected")
            
    finally:
        recorder.cleanup()