# init at each windows powershell session
# $Env:HF_TOKEN = "TOKEN"

import os
from huggingface_hub import InferenceClient


client = InferenceClient(
    provider="hf-inference",
    api_key=os.environ["HF_TOKEN"],
)

result = client.translation(
    "Today is a sunny day.",
    model="google-t5/t5-small",
    src_lang="en",
    tgt_lang="de"
)

print("German translation:", result["translation_text"])