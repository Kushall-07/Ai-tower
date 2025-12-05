import os
from typing import Optional, TypedDict

from dotenv import load_dotenv
from groq import Groq

from .scrubber import scrub_text

load_dotenv()


class LLMResult(TypedDict):
    text: str
    model: str
    error: Optional[str]


GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY not set. safe_generate() will return placeholder responses.")
    client: Optional[Groq] = None
else:
    client = Groq(api_key=GROQ_API_KEY)


def safe_generate(prompt: str) -> LLMResult:
    """
    Security-aware wrapper around the LLM.
    Returns:
        {
          "text": <model output or fallback>,
          "model": <model name or "placeholder">,
          "error": <error string or None>
        }
    """

    safe_prompt = scrub_text(prompt or "")

    # No client => placeholder mode
    if client is None:
        return {
            "text": f"(Placeholder LLM response for safe prompt: {safe_prompt})",
            "model": "placeholder",
            "error": "GROQ_API_KEY not set",
        }

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": safe_prompt,
                }
            ],
            temperature=0.3,
            max_tokens=256,
        )

        text = response.choices[0].message.content or ""
        return {
            "text": text,
            "model": "llama-3.1-8b-instant",
            "error": None,
        }

    except Exception as e:
        print(f"[safe_generate] Error calling Groq: {e}")
        return {
            "text": f"(Error calling LLM, fallback response for safe prompt: {safe_prompt})",
            "model": "llama-3.1-8b-instant",
            "error": str(e),
        }
