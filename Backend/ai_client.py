"""
This module provides an OpenAI-backed refactoring engine that always calls the API
and returns a structured JSON object with the refactored code and a short explanation.
We use the Responses API with a JSON Schema so outputs are predictable and safe to parse.
A cached client avoids re-initializing the SDK on each request, and missing credentials
raise a clear error that the API layer can translate into an HTTP 503.
"""

import os
import json
from typing import Dict, List

# Cached client instance so we don't re-create it on every request.
_openai_client = None


def _get_openai_client() -> "OpenAI":
    """
    Construct and cache the OpenAI client. If the API key is unavailable, an error is
    raised to enable the web layer to return a meaningful HTTP 503 response.
    """
    global _openai_client
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        # This exact message is used by the API layer to decide on 503.
        raise RuntimeError("OPENAI_API_KEY is required for refactoring")

    if _openai_client is None:
        # Import only when needed so local tooling doesn't require the package until used.
        from openai import OpenAI
        _openai_client = OpenAI(api_key=key)
    return _openai_client


# JSON Schema used for structured outputs so the model must return
# exactly {"refactored_code": str, "explanation": str} and nothing else.
_REF_SCHEMA: dict = {
    "name": "RefactorOutput",
    "schema": {
        "type": "object",
        "properties": {
            "refactored_code": {"type": "string"},
            "explanation": {"type": "string"},
        },
        "required": ["refactored_code", "explanation"],
        "additionalProperties": False,
    },
    "strict": True,
}


def _call_openai(*, source: str, language: str, goals: List[str]) -> Dict[str, str]:
    """
    Send the code and goals to OpenAI using the Responses API with Structured Outputs.
    Return the parsed dictionary so the Flask endpoint function that handles the request
    can turn it into JSON and send the response.
    """
    client = _get_openai_client()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    goals_txt = ", ".join(goals) if goals else "readability"

    # Clear instructions keep the model on task and focused on JSON only.
    system = (
        "Refactor the code safely. Preserve behavior and improve clarity."
        "Simplify only when you are certain the result behaves the same."
        "Follow the conventions of the language. Return only the JSON object"
        "defined by the schema. Do not include any extra text."
    )

    user_text = (
        f"Language: {language}\n"
        f"Goals: {goals_txt}\n\n"
        f"Refactor the following code and explain the key improvements:\n"
        f"```{language}\n{source}\n```"
    )

    response = client.responses.create(
        model=model, temperature=0.2,  # Low temperature for consistent refactors
        response_format={"type": "json_schema", "json_schema": _REF_SCHEMA},
        input=[{"role": "system", "content": system},
               {"role": "user", "content": [{"type": "input_text", "text": user_text}]},],
    )

    # The SDK returns a convenience string that we can parse as JSON and convert
    # into our expected structure.
    payload = json.loads(response.output_text)
    return {
        "refactored_code": payload["refactored_code"],
        "explanation": payload["explanation"],
    }


def invoke_refactor_engine(*, source: str, language: str = "python", goals: List[str] | None = None) -> Dict[str, str]:
    """
    This is the public entry point. It always routes requests through OpenAI and lets
    errors surface to the caller. The caller maps exceptions, including missing keys,
    to HTTP status codes.
    """
    goals = goals or ["readability"]
    return _call_openai(source=source, language=language, goals=goals)
