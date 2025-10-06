import os
import re
import json
from typing import Dict, List, Optional

def _perform_basic_refactor(text: str) -> str:
    s = text.replace("\r\n", "\n").replace("\r", "\n")
    s = s.replace("\t", "    ")
    s = "\n".join(line.rstrip() for line in s.split("\n"))
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s

def _build_explanation(goals: List[str], language: str, before: str, after: str) -> str:
    changes: list[str] = []
    if "\t" in before and "\t" not in after:
        changes.append("replaced tabs with 4 spaces")
    if any(line.rstrip() != line for line in before.splitlines()):
        changes.append("removed trailing whitespace")
    if re.search(r"\n{3,}", before) and not re.search(r"\n{3,}", after):
        changes.append("collapsed extra blank lines")
    if not changes:
        changes.append("minor formatting cleanup")
    goals_txt = ", ".join(goals) if goals else "readability"
    return f"I applied minor formatting for {language} code: " + "; ".join(changes) + f". Goals: {goals_txt}."

# OpenAI integration 

_openai_client = None

def _get_openai_client() -> Optional["OpenAI"]:
    """
    Create the OpenAI client if OPENAI_API_KEY is present.
    Returns None if the key is missing so callers can fall back locally.
    """
    global _openai_client
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    if _openai_client is None:
        from openai import OpenAI  # import only if we actually need it
        _openai_client = OpenAI(api_key=key)
    return _openai_client

# JSON Schema the model must follow (Structured Outputs)
_REF_SCHEMA: dict = {
    "name": "RefactorOutput",
    "schema": {
        "type": "object",
        "properties": {
            "refactored_code": {"type": "string"},
            "explanation": {"type": "string"}
        },
        "required": ["refactored_code", "explanation"],
        "additionalProperties": False,
    },
    "strict": True,
}

def _call_openai(*, source: str, language: str, goals: List[str]) -> Dict[str, str]:
    """
    Calls OpenAI Responses API with Structured Outputs and returns the parsed dict.
    """
    client = _get_openai_client()
    if client is None:
        raise RuntimeError("OPENAI_API_KEY not set")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    goals_txt = ", ".join(goals) if goals else "readability"

    system = (
        "You are a senior software engineer. Refactor code safely. "
        "Preserve behavior, simplify where possible, remove dead code, and apply idiomatic style. "
        "Return ONLY the JSON object described by the provided schema."
    )
    user_text = (
        f"Language: {language}\n"
        f"Goals: {goals_txt}\n\n"
        f"Refactor the following code and explain the key improvements:\n"
        f"```{language}\n{source}\n```"
    )

    # Use the Responses API and force JSON that matches our schema
    response = client.responses.create(
        model=model,
        temperature=0.2,
        response_format={"type": "json_schema", "json_schema": _REF_SCHEMA},
        input=[{"role": "system", "content": system},
               {"role": "user",   "content": [{"type": "input_text", "text": user_text}]}],
    )

    # The SDK exposes a convenience string; we then JSON-parse it.
    text = response.output_text
    payload = json.loads(text)
    return {
        "refactored_code": payload["refactored_code"],
        "explanation": payload["explanation"],
    }

# Public entry point

def invoke_refactor_engine(*, source: str, language: str = "python", goals: List[str] | None = None) -> Dict[str, str]:
    goals = goals or ["readability"]
    # Try OpenAI first; if anything fails, fall back to the local formatter.
    try:
        return _call_openai(source=source, language=language, goals=goals)
    except Exception:
        refactored: str = _perform_basic_refactor(source)
        explanation: str = _build_explanation(goals, language, source, refactored)
        return {"refactored_code": refactored, "explanation": explanation}ai_client.py
