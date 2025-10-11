import os
from openai import OpenAI

# init at each windows powershell session
# $Env:HF_TOKEN = "TOKEN"

class GermanTutor:
    """
    A simple terminal-friendly German tutor using a chat LLM.
    """

    def __init__(self, api_key_env: str = "HF_TOKEN", 
                        base_url: str = "https://router.huggingface.co/v1", 
                        model: str = "deepseek-ai/DeepSeek-R1:fireworks-ai"):
        """
        Initialize the GermanTutor with OpenAI client settings.

        :param api_key_env: Name of the environment variable storing the API key.
        :param base_url: Base URL for the chat API.
        :param model: The LLM model identifier to use.
        """
        # Step 1: Get the API token from environment variable
        token = os.getenv(api_key_env)
        if not token:
            raise ValueError(f"Environment variable '{api_key_env}' not set.")

        # Step 2: Initialize the OpenAI client with base URL and API key
        self.client = OpenAI(
            base_url=base_url,
            api_key=token,
        )
        # Step 3: Store the model identifier
        self.model = model

    def correct(self, sentence: str) -> None:
        """
        Send the user's German sentence to the model and print corrections and advice.

        :param sentence: The raw German sentence to correct.
        """
        # Step 1: Build system and user messages for the LLM prompt
        system_msg = (
            "You are a friendly, expert German tutor. "
            "When given a user's German sentence, you must:\n"
            "1. Provide a corrected version of their sentence.\n"
            "2. Explain each correction in plain bullet points, focusing on grammar rules.\n"
            "3. Offer at least two style or word-choice suggestions to make the sentence more natural.\n"
            "4. Keep your explanations concise and in English."
        )
        user_msg = (
            f"Here is the German sentence: '{sentence}'\n\n"
            "Please correct it and provide explanations and tips."
        )

        # Step 2: Call the chat completion endpoint with the constructed messages
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
        )

        # Step 3: Extract the assistant's response from the API output
        content = response.choices[0].message.content

        # Step 4: Print terminal-friendly output
        print("\n--- Correction & Feedback ---\n")
        # Step 5: Remove markdown formatting if any (simple strip of markdown bullets and backticks)
        clean = content.replace("**", "").replace("`", "")
        print(clean)


if __name__ == "__main__":
    # Example usage
    # Step 1: Create an instance of GermanTutor
    tutor = GermanTutor()
    # Step 2: Prompt user for a German sentence
    raw = input("Enter a German sentence to correct: ")
    # Step 3: Call the correct method to get feedback
    tutor.correct(raw)
