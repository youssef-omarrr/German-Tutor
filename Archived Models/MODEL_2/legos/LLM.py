import os
import re
from typing import Tuple
from openai import OpenAI

# init at each windows powershell session
# $Env:HF_TOKEN = "TOKEN"

class GermanTutor:
    """
    A simple terminal-friendly German tutor using a chat LLM.
    """

    def __init__(self, api_key_env: str = "HF_TOKEN", 
                        base_url: str = "https://router.huggingface.co/v1", 
                        model: str = "openai/gpt-oss-120b:cerebras"):
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
        
    def clean_input(self, text: str) -> Tuple[str, str]:
        """A function that changes the input markdown into better formated text and a list of strings for the tts 

        Args:
            text (str): markdown like text

        Returns:
            Tuple (clean_text, plain_tts_text)
        """
        # Remove Markdown formatting completely
        clean = text
        clean = re.sub(r"^#+\s*", "", clean, flags=re.MULTILINE)  # headings
        clean = re.sub(r"(\*\*|__)(.*?)\1", r"\2", clean)        # bold
        clean = re.sub(r"(\*|_)(.*?)\1", r"\2", clean)           # italic
        clean = re.sub(r"`([^`]*)`", r"\1", clean)               # inline code
        clean = re.sub(r"^>\s*", "", clean, flags=re.MULTILINE)  # blockquotes
        
        
        # Remove dashes by replacing them with spaces BEFORE filtering allowed chars
        clean = clean.replace("-", " ")
        
        # Normalize special quotes to simple ASCII quotes
        clean = clean.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")

        # Keep letters, numbers, spaces, commas, periods, apostrophes, colons only
        # Preserve commas and periods to keep natural TTS pauses
        plain_tts = re.sub(r"[^a-zA-Z0-9äöüÄÖÜß\s,.'\":]", "", clean)
        
        # Replace slashes '/' with ' slash ' (spaces around for clarity)
        plain_tts = plain_tts.replace("/", " slash ")

        # Normalize whitespace after all replacements
        plain_tts = re.sub(r"\s+", " ", plain_tts).strip()
        
        # Replace numbered list prefixes like '1. Alternative:' with 'Alternative one:', '2. Alternative:' with 'Alternative two:', etc.
        def replace_numbered_alternatives(match):
            number = match.group(1)
            word = self.number_to_word(number)
            # We keep the rest of the line after the number and dot + space
            rest = match.group(2)
            return f"Alternative {word}:{rest}"

        plain_tts = re.sub(r"\b(\d{1,2})\. Alternative(:)", replace_numbered_alternatives, plain_tts)

        # Remove escaped quotes around phrases like "Auf Wieder" (turn \"Auf Wieder\" into Auf Wieder)
        plain_tts = re.sub(r'\\"(.*?)\\"', r'\1', plain_tts)
        
        # Format clean text as a multiline Python string literal split by full stops,
        # except those after numbers and those that are part of common abbreviations like e.g.
        plain_tts = self.format_for_tts(plain_tts)
        
        return clean, plain_tts
    
    def number_to_word(self, num_str):
        # Map numbers 1-10 to words
        mapping = {
            '1': 'one',
            '2': 'two',
            '3': 'three',
            '4': 'four',
            '5': 'five',
            '6': 'six',
            '7': 'seven',
            '8': 'eight',
            '9': 'nine',
            '10': 'ten'
        }
        return mapping.get(num_str, num_str)  # fallback to number if not in mapping

    def format_for_tts(self, text: str) -> str:
        """
        Format the input text by splitting after every full stop '.' except when the full stop
        is part of a number like '1.', '2.', or part of abbreviations like 'e.g.' or 'i.e.'
        and also split after every colon ':'.
        """
        
        # Regex explanation:
        # Split on either:
        # 1) a full stop not preceded by digit and not part of abbrev like e.g.  --> (?<!\d)\.(?!\s*[a-z]\.)
        # 2) OR on a colon ':'
        # consume any following whitespace in either case
        split_pattern = r'(?<!\d)\.(?!\s*[a-z]\.)\s*|:\s*'

        parts = re.split(split_pattern, text.strip())

        # We lost the punctuation on split, so we add it back except for the colon case (we add ':' back manually)
        # We detect if the split point was a colon or period by searching for ':' or '.' in the original text?
        # Instead, simpler: after splitting, re-add punctuation based on original text.
        # But regex lost punctuation. So just add '.' to all except last if original text ended with punctuation.

        # Safer approach: Use findall to get all separators and pair them with parts

        # Find all splitters (either '.' or ':')
        splitters = re.findall(r'(?<!\d)\.(?!\s*[a-z]\.)|:', text.strip())

        # Add punctuation back to each part except last (which may have no punctuation)
        sentences = []
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            if i < len(splitters):
                # add the punctuation that was matched
                punctuation = splitters[i]
                sentences.append(part + punctuation)
            else:
                sentences.append(part)

        # Add a space after each sentence if not present to preserve spacing
        sentences = [s if s.endswith(' ') else s + " " for s in sentences]

        # Build the multiline string literal
        result = "(\n"
        for s in sentences:
            s_escaped = s.replace('"', ' ')
            result += f'    "{s_escaped}"\n'
        result += ")"
        return result

    def correct(self, sentence: str) -> None:
        """
        Send the user's German sentence to the model and print corrections and advice.

        :param sentence: The raw German sentence to correct.
        
        :return: Tuple (clean_text, plain_tts_text)
        """
        # Step 0: Capitalize the first letter of the input (becaue the STT doesn't for some reason...)
        sentence = sentence[0].upper() + sentence[1:]
        
        # Step 1: Build system and user messages for the LLM prompt
        system_msg = (
            "ROLE & CONTEXT:\n"
            "You are a friendly, highly skilled German language tutor for an A1-level student. "
            "Your main task is to help the student improve their German or English sentences "
            "by correcting, translating, and explaining them clearly.\n\n"

            "PRIMARY OBJECTIVES:\n"
            "1. Detect the input language (German or English) and check if it is related to learning these languages.\n"
            "2. If related to German learning:\n"
            "   - If in German:\n"
            "       • If correct: Say exactly: The phrase \"<sentence>\" is correct.\n"
            "         - DO NOT include a 'Corrected Sentence' section.\n"
            "       • If incorrect: Provide a 'Corrected Sentence:' line with the fixed version.\n"
            "   - If in English: Provide the correct German equivalent.\n"
            "   - Always provide an 'Explanation:' section with simple, clear bullet points explaining:\n"
            "       • Grammar points\n"
            "       • Word choice\n"
            "       • Common pitfalls for A1 learners\n"
            "   - Always give at least TWO alternative sentences labeled 'Alternative 1:' and 'Alternative 2:', both suitable for A1 learners.\n\n"

            "3. If the input is NOT related to learning German or English:\n"
            "   - Drop the tutor persona and act as a knowledgeable assistant.\n"
            "   - Start the answer with: 'Okay sir, here is what I found about [question]:' or something along this line.\n"
            "   - Then provide a helpful, accurate, and concise response.\n\n"
            "4. add an encouraging message at the end."

            "FORMATTING RULES:\n"
            "- Keep responses concise but complete — short input → short output, long input → longer output.\n"
            "- Preserve punctuation in explanations and alternatives.\n"
            "- Use polite, encouraging language for language-related help.\n"
            "- End all section headers with a colon.\n"
            "- Use Markdown for structure:\n"
            "  **Corrected Sentence:**\n"
            "  **Explanation:**\n"
            "  **Alternative 1:**\n"
            "  **Alternative 2:**\n\n"

            "OUTPUT CONSISTENCY:\n"
            "- Never invent unrelated examples.\n"
            "- Always keep language level A1 for language-related answers.\n"
            "- No extra prefaces like 'Sure!' — start directly with the required sections."
        )

        user_msg = (
            f"Here is the student's sentence or question: '{sentence}'\n"
            "If it's German/English learning related, follow the tutor rules above.\n"
            "If not, drop the tutor role and answer my question starting with: 'Okay sir, here is what I found about [question]:'."
        )

        # Step 2: Call the chat completion endpoint with improved parameters
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.2,        # low temp for accuracy
            max_tokens=500,         # enough space for detailed explanations
            presence_penalty=0.0,   # no forced novelty
            frequency_penalty=0.0   # don't penalize repetition if needed
        )


        # Step 3: Extract the assistant's response from the API output
        content = response.choices[0].message.content

        # Step 4: Print terminal-friendly output
        print("\n--- Correction & Feedback ---\n")
        
        # Step 5: Remove markdown formatting if any (simple strip of markdown bullets and backticks)
        # Step 6: Create plain text for TTS (remove newlines, punctuation, special chars)
        clean, plain_tts = self.clean_input(content)

        # Step 7: Return both
        return clean, plain_tts


if __name__ == "__main__":
    # Example usage
    # Step 1: Create an instance of GermanTutor
    tutor = GermanTutor()
    # Step 2: Prompt user for a German sentence
    raw = input("Enter a German sentence to correct: ")
    # Step 3: Call the correct method to get feedback
    clean, plaint_tts = tutor.correct(raw)
    print(clean)
    print("===========================================================")
    print(plaint_tts)
