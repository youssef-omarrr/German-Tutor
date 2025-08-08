import torch
from TTS.api import TTS
import playsound


# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# # List available 🐸TTS models
# for model in TTS().list_models():
#     print(model)

# Pick a model
# model_name = "tts_models/multilingual/multi-dataset/your_tts"
# model_name = "tts_models/deu/fairseq/vits"
model_name = "tts_models/multilingual/multi-dataset/bark"

# # High-quality multilingual model (NEEDS CLONING)
# model_name = "tts_models/multilingual/multi-dataset/xtts_v2"

# Init TTS
tts = TTS(model_name).to(device)
print(tts.speakers)
print(tts.languages)
output_path = "output.wav"

# Run TTS (no speaker_wav needed)
tts.tts_to_file(
    text="Hello! Wie geht es dir? this is just a test",
    file_path= output_path ,
    # language= 'en',
    # speaker=tts.speakers[0]  # pick first available speaker
)

# Play audio
playsound.playsound(output_path)