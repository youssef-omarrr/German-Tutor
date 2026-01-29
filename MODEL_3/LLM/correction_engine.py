from groq import Groq
from dotenv import load_dotenv
import os
from prompt_templates import create_prompt_template
from response_formatter import ResponseFormatter

# load .env file t0 get access keys
load_dotenv()

class GermanTutor:
    def __init__(self,
                model = "llama-3.3-70b-versatile",
                ):
        """
        other options for model:
            - llama-3.3-70b-versatile (Best for German)
            - llama-3.1-8b-instant (Faster, less accurate)
            - mixtral-8x7b-32768 (Good alternative)
        """
        self.model = model
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
    def response(self,
                prompt):
        
        response = self.client.chat.completions.create(
            model= self.model,
            messages=create_prompt_template(prompt),
            temperature = 0.9,
            max_tokens = 500
        )
        
        response = response.choices[0].message.content
        print(response)
        return response
    

# ======================================================================== #
#                              TESTING                                     #
# ======================================================================== #

if __name__ == "__main__":
    model = GermanTutor()

    # Test cases
    test_inputs = [
        "Ich habe gestern ins Kino gegangen",  # German correction
        "How do you say 'I love you' in French?",  # Translation request
        "What's the capital of Japan?",  # General question
        "Explain German articles",  # Language concept
        "わたしは学生です correct?",  # Japanese check
    ]
    
    model.response(test_inputs[0])
