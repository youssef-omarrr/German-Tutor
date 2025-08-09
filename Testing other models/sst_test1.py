from huggingface_hub import InferenceClient
import queue
import threading
import time
import io
import os
import inspect
import sounddevice as sd
import soundfile as sf
import numpy as np

SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SECONDS = 4.0
OVERLAP_SECONDS = 0.5

PROVIDER="fal-ai"
HF_TOKEN = os.environ.get("HF_TOKEN")  # set HF_TOKEN in env
MODEL_ID = "openai/whisper-large-v3"

client = InferenceClient(
    provider=PROVIDER,
    api_key=HF_TOKEN,
)

q = queue.Queue()
buffer = np.zeros((0, CHANNELS), dtype='float32')

def audio_callback(indata, frames, time_info, status):
    global buffer
    if status:
        print("Status:", status)
    buffer = np.concatenate((buffer, indata.copy()), axis=0)
    needed = int(CHUNK_SECONDS * SAMPLE_RATE)
    if buffer.shape[0] >= needed:
        chunk = buffer[:needed]
        keep = int(OVERLAP_SECONDS * SAMPLE_RATE)
        buffer = buffer[needed - keep:]
        q.put(chunk)

def worker_api():
    idx = 0
    # we'll prepare the default params we want to send
    asr_params = {"language": "de", "task": "transcribe"}

    # detect supported kwarg name on the installed client version
    sig = inspect.signature(client.automatic_speech_recognition)
    supports_parameters = "parameters" in sig.parameters
    supports_extra_body = "extra_body" in sig.parameters

    while True:
        chunk = q.get()
        if chunk is None:
            break
        idx += 1

        # write WAV to BytesIO and get raw bytes (HF client expects bytes)
        bio = io.BytesIO()
        sf.write(bio, chunk, SAMPLE_RATE, format="WAV")
        audio_bytes = bio.getvalue()

        start = time.time()
        try:
            if supports_parameters:
                out = client.automatic_speech_recognition(audio_bytes, model=MODEL_ID, parameters=asr_params)
            elif supports_extra_body:
                out = client.automatic_speech_recognition(audio_bytes, model=MODEL_ID, extra_body=asr_params)
            else:
                # fallback: call without extra params (will rely on auto-detect)
                out = client.automatic_speech_recognition(audio_bytes, model=MODEL_ID)
        except Exception as e:
            print(f"[chunk {idx}] API error:", repr(e))
            q.task_done()
            continue

        latency = time.time() - start

        # parse output robustly — HF may return dict or object with .text
        text = None
        if isinstance(out, dict):
            # common keys: "text", "result", sometimes nested
            text = out.get("text") or out.get("result") or out.get("transcription")
        else:
            # dataclass-like object: try .text then fallback to str()
            text = getattr(out, "text", None) or getattr(out, "result", None) or str(out)

        # final fallback to string representation
        text = text if text is not None else str(out)

        print(f"[chunk {idx}] api latency {latency:.2f}s -> {text}")
        q.task_done()


def main():
    worker = threading.Thread(target=worker_api, daemon=True)
    worker.start()
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=audio_callback, dtype='float32'):
        print("Listening (HF API). Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Stopping.")
    q.put(None)
    worker.join()

if __name__ == "__main__":
    main()
