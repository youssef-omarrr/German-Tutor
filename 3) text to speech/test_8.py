import torch
from TTS.api import TTS
import playsound

print("testing something here")

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# # List available 🐸TTS models
# for model in TTS().list_models():
#     print(model)

# High-quality multilingual model (NEEDS CLONING)
model_name = "tts_models/multilingual/multi-dataset/xtts_v2"

# Init TTS
tts = TTS(model_name).to(device)


# print speakers and languages
# for speaker in tts.speakers:
#     print(speaker)
# for lan in tts.languages:
#     print(lan)


for i, speaker in enumerate(tts.speakers):
    output_path = f"testing_speakers/ output_{i}.wav"

    # Run TTS (no speaker_wav needed)
    tts.tts_to_file(
        text = (
            "Hello! Wie geht es dir? "
            "Heute ist ein schöner Tag, and I'm glad we can practice together. "
            "I bought coffee this morning und ein frisches Brötchen. "
            "If you have any questions, frag mich bitte. "
            "Let's try a short exercise now."
        ),
        file_path= output_path ,
        language= 'de',
        speaker=speaker
    )

# # Play audio
# playsound.playsound(output_path)