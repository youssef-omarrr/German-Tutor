import os
from openai import OpenAI

# 1) Instantiate your client
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv("HF_TOKEN"),
)

# 2) Your dynamic German input
USER_INPUT = "ich bin gut"

# 3) Build the messages list, injecting USER_INPUT via an f-string
messages = [
    {
        "role": "system",
        "content": (
            "You are a friendly, expert German tutor. "
            "When given a user’s German sentence, you must:\n"
            "1. Provide a corrected version of their sentence.\n"
            "2. Explain each correction in bullet points, "
            "   focusing on grammar rules (e.g. cases, word order, verb conjugation).\n"
            "3. Offer at least two style or word-choice suggestions "
            "   to make the sentence more natural or advanced.\n"
            "4. Keep your explanations concise and in English."
        )
    },
    {
        "role": "user",
        # <-- f-string injection happens here -->
        "content": (
            f"Hier ist mein deutscher Satz:\n"
            f"“{USER_INPUT}”\n\n"
            "Bitte korrigiere ihn und gib dir dazu Erklärungen und Tipps."
        )
    }
]

response = client.chat.completions.create(
    model="openai/gpt-oss-120b:cerebras",
    messages=messages
)


print(response.choices[0].message.content)