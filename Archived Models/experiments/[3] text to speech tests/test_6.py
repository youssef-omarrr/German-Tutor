import os
import time
import torch
from TTS.api import TTS

# Playback fallback imports
import sys
import subprocess

# Windows builtin player
try:
    import winsound
except Exception:
    winsound = None
    
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------
# Config
# ---------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = "tts_models/multilingual/multi-dataset/bark"  # change if you want
text = "Hello! Wie geht es dir? This is just a test."

# Output file (use absolute path to avoid MCI quoting problems)
output_path = os.path.abspath("output.wav")

# ---------------------------
# Load model and synthesize
# ---------------------------
print("Loading model (this can take a while the first run)...")
tts = TTS(model_name).to(device)

# If model is multi-speaker, pick a sensible default speaker.
kwargs = {}
speakers = getattr(tts, "speakers", None)
if speakers:
    kwargs["speaker"] = speakers[0]

# If model exposes languages, try to pick German or default
languages = getattr(tts, "languages", None)
if languages:
    preferred = None
    for candidate in ("de-DE", "de", "de_de", "de-de"):
        if candidate in languages:
            preferred = candidate
            break
    kwargs["language"] = preferred if preferred is not None else languages[0]

print("Synthesizing to:", output_path)
tts.tts_to_file(text=text, file_path=output_path, **kwargs)

# Wait until the file is available for reading (safety on some platforms)
for i in range(10):
    if os.path.exists(output_path):
        try:
            with open(output_path, "rb"):
                break
        except PermissionError:
            time.sleep(0.1)
    else:
        time.sleep(0.1)
else:
    raise RuntimeError("Failed to write output file or file remains locked.")

print(f"Saved audio to {output_path}")

# ---------------------------
# Playback (Windows-first)
# ---------------------------
def play_windows(path: str):
    """Try winsound (preferred), else os.startfile."""
    # Try winsound if available
    if winsound:
        try:
            # Blocking playback using WinAPI (does not use MCI text commands)
            winsound.PlaySound(path, winsound.SND_FILENAME)
            return True
        except Exception as e:
            print("winsound playback failed:", e)

    # Fallback: open with default application (non-blocking)
    try:
        os.startfile(path)
        return True
    except Exception as e:
        print("os.startfile fallback failed:", e)
        return False

def play_cross_platform(path: str):
    """Open file with default app on other platforms."""
    if sys.platform.startswith("win"):
        return play_windows(path)
    if sys.platform == "darwin":
        subprocess.Popen(["open", path])
        return True
    # Linux
    subprocess.Popen(["xdg-open", path])
    return True

# Attempt playback
if not play_cross_platform(output_path):
    print("Playback failed. You can open the file manually at:", output_path)
