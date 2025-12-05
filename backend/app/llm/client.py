import os
from typing import Optional

from dotenv import load_dotenv
from groq import Groq

from .scrubber import scrub_text

# Load .env file so GROQ_API_KEY is available
load_dotenv()

GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    # We don't crash here -> placeholder mode if key not set
    print("WARNING: GROQ_API_KEY not set. safe_generate() will return placeholder responses.")
    client = None
else:
    client = Groq(api_key=GROQ_API_KEY)


def safe_generate(prompt: str) -> str:
    """
    Security-aware wrapper around the LLM.
    - Scrubs sensitive data
    - Calls Groq Llama 3 if key is available
    - Falls back to placeholder if something fails
    """

    # 1) Scrub sensitive data first
    safe_prompt = scrub_text(prompt or "")

    # 2) If no client (no key), return placeholder
    if client is None:
        return f"(Placeholder LLM response for safe prompt: {safe_prompt})"

    try:
        # 3) Call Groq's Llama 3 model
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # or "llama3-8b-8192" for cheaper
            messages=[
                {
                    "role": "user",
                    "content": safe_prompt,
                }
            ],
            temperature=0.3,
            max_tokens=256,
        )

        content = response.choices[0].message.content
        return content

    except Exception as e:
        # 4) Fail safe – never crash the app, just log and fallback
        print(f"[safe_generate] Error calling Groq: {e}")
        return f"(Error calling LLM, fallback response for safe prompt: {safe_prompt})"
