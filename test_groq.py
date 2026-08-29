import os
from groq import Groq

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is not set")

print("Groq API key found:", api_key[:8] + "...")

client = Groq(api_key=api_key)

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "system",
            "content": "You are the AI analysis assistant for NetSentinel."
        },
        {
            "role": "user",
            "content": "Analyze this network test result: latency=120ms, packet_loss=5%, error_rate=3%. Give a short recommendation."
        }
    ]
)

print("\n=== NetSentinel AI Analysis ===")
print(response.choices[0].message.content)
