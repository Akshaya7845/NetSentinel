import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from src.ai.prompt_builder import PromptBuilder


class LLMService:
    """
    Connects NetSentinel with Gemini AI
    using LangChain.
    """

    def __init__(self):

        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.3,
        )

        self.prompt_builder = PromptBuilder()

    def generate_executive_report(self):
        """
        Generates the Executive Summary.
        """

        prompt = self.prompt_builder.build_executive_prompt()

        response = self.llm.invoke(prompt)

        return response.content

    def generate_detailed_report(self):
        """
        Generates the Detailed Technical Report.
        """

        prompt = self.prompt_builder.build_detailed_prompt()

        response = self.llm.invoke(prompt)

        return response.content