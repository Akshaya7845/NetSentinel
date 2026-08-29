import os

from dotenv import load_dotenv
from groq import Groq

from src.ai.prompt_builder import PromptBuilder


class LLMService:
    """
    Connects NetSentinel with Groq AI.
    """

    def __init__(self):

        load_dotenv()

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. Please check your .env file."
            )

        self.client = Groq(api_key=api_key)

        # Groq model that you successfully tested
        self.model = "openai/gpt-oss-20b"

        self.prompt_builder = PromptBuilder()

    def generate_text(self, prompt):
        """
        Generates AI output for any custom prompt.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.3,
        )

        return response.choices[0].message.content

    def generate_executive_report(self):
        """
        Generates the Executive Summary.
        """

        prompt = self.prompt_builder.build_executive_prompt()

        return self.generate_text(prompt)

    def generate_detailed_report(self):
        """
        Generates the Detailed Technical Report.
        """

        prompt = self.prompt_builder.build_detailed_prompt()

        return self.generate_text(prompt)