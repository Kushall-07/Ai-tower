import os
import json
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client: Optional[Groq] = None
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)


def _strip_json_fences(text: str) -> str:
    """
    Remove ```json ... ``` or ``` ... ``` fences if present.
    """
    text = text.strip()
    if text.startswith("```"):
        # remove first line (``` or ```json)
        lines = text.splitlines()
        if len(lines) >= 2:
            # drop first and last if last is ```
            if lines[-1].strip().startswith("```"):
                lines = lines[1:-1]
            else:
                lines = lines[1:]
            text = "\n".join(lines).strip()
    return text


def _parse_json_safe(raw: str) -> Any:
    """
    Try to parse JSON; on failure, return None instead of raising.
    """
    try:
        cleaned = _strip_json_fences(raw)
        return json.loads(cleaned)
    except Exception:
        return None


def _extract_actions_with_llm(prompt: str, answer: str) -> List[Dict[str, Any]]:
    """
    Optional second LLM pass to extract structured actions from
    (prompt, answer). If anything fails, returns [].
    """
    if client is None:
        return []

    try:
        system_msg = (
            "You are an AI that extracts structured ACTION suggestions for an "
            "enterprise control tower.\n\n"
            "Given the user's prompt and the assistant's answer, return a JSON object "
            "with this exact schema:\n\n"
            "{\n"
            '  "actions": [\n'
            "    {\n"
            '      "type": "email_suggestion" | "database_query" | "api_call_external" '
            '| "notification" | "file_operation" | "other",\n'
            '      "payload": { ... arbitrary JSON fields ... }\n'
            "    }\n"
            "  ]\n"
            "}\n\n"
            "- Only include actions that an enterprise system might reasonably execute.\n"
            "- If there are no clear actions, return {\"actions\": []}.\n"
            "- ALWAYS return valid JSON. No explanations, no comments."
        )

        user_msg = (
            "User prompt:\n"
            f"{prompt}\n\n"
            "Assistant answer:\n"
            f"{answer}\n\n"
            "Now return the JSON object:"
        )

        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.2,
        )

        content = resp.choices[0].message.content
        data = _parse_json_safe(content or "")
        if not isinstance(data, dict):
            return []
        actions = data.get("actions", [])
        if not isinstance(actions, list):
            return []
        # Basic sanity: each action should be dict with type + payload
        cleaned: List[Dict[str, Any]] = []
        for a in actions:
            if not isinstance(a, dict):
                continue
            a_type = a.get("type") or "other"
            payload = a.get("payload") or {}
            if not isinstance(payload, dict):
                payload = {}
            cleaned.append({"type": a_type, "payload": payload})
        return cleaned
    except Exception:
        # If anything fails, just return no actions
        return []


def safe_generate(prompt: str) -> Dict[str, Any]:
    """
    Secure wrapper around the LLM.

    Returns a dict:
    {
        "text": <answer or fallback>,
        "model": <model_name or "unknown">,
        "actions": [ { "type": str, "payload": dict }, ... ],
        "error": <error message or None>
    }
    """
    if client is None:
        # No API key, just echo prompt
        return {
            "text": f"(LLM not configured) Echo: {prompt}",
            "model": "none",
            "actions": [],
            "error": "GROQ_API_KEY not set",
        }

    base_system = (
        "You are a secure enterprise assistant. "
        "You MUST avoid leaking secrets, credentials, or personal data. "
        "Respond clearly and concisely."
    )

    try:
        # Main answer call
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": base_system},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        model_name = resp.model or "llama-3.1-8b-instant"
        answer = resp.choices[0].message.content or ""

        # Second pass: extract structured actions (best-effort)
        actions = _extract_actions_with_llm(prompt, answer)

        return {
            "text": answer,
            "model": model_name,
            "actions": actions,
            "error": None,
        }

    except Exception as e:
        # Fallback on any error
        return {
            "text": f"(Error calling LLM, fallback response for prompt: {prompt})",
            "model": "unknown",
            "actions": [],
            "error": str(e),
        }
