import os
import pytest
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


@pytest.mark.skipif(
    not GROQ_API_KEY,
    reason="GROQ_API_KEY is not configured"
)
def test_groq_connection():

    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": "Respond with exactly: Groq connection successful"
            }
        ],
        temperature=0,
    )

    result = response.choices[0].message.content

    assert result is not None
    assert len(result.strip()) > 0