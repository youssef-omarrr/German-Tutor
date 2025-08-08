import os
import torch
from TTS.api import TTS
import winsound   # Windows only

device = "cuda" if torch.cuda.is_available() else "cpu"

# Try these (one at a time or both to compare)
models = {
    "german": "tts_models/de/thorsten/vits",        # good German single-speaker
    "german_fairseq": "tts_models/deu/fairseq/vits",# single-speaker fairseq vits (if available)
}

for name, model_name in models.items():
    try:
        print("Loading", model_name)
        tts = TTS(model_name).to(device)
    except Exception as e:
        print("Failed to load", model_name, e)
        continue

    out = os.path.abspath(f"test_{name}.wav")
    # If model is multi-speaker, pick first speaker to avoid failures:
    kwargs = {}
    if getattr(tts, "speakers", None):
        kwargs["speaker"] = tts.speakers[0]
    if getattr(tts, "languages", None):
        kwargs["language"] = tts.languages[0]

    text = "Guten Morgen, wie geht es dir? Hello, how are you?"
    tts.tts_to_file(text=text, file_path=out, **kwargs)
    print("Saved", out)
    winsound.PlaySound(out, winsound.SND_FILENAME)
