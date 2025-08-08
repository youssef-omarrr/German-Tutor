import sounddevice as sd  # pip install sounddevice
import soundfile as sf    # pip install soundfile

def record_voice(output_path="speaker.wav", duration=10, sample_rate=16000):
    """
    Records your voice from the microphone and saves it as a WAV file.

    :param output_path: Path to save the recorded audio.
    :param duration: Duration in seconds.
    :param sample_rate: Sample rate in Hz (16000 recommended for XTTS).
    """
    print(f"Recording for {duration} seconds... Speak naturally.")
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,        # mono
        dtype="int16"      # 16-bit PCM
    )
    sd.wait()  # Wait until recording is finished
    sf.write(output_path, recording, sample_rate)
    print(f"✅ Recording saved to {output_path}")

if __name__ == "__main__":
    record_voice(output_path="my_voice.wav", duration=10)
