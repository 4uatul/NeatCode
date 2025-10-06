"""
API tests for the Flask backend. We patch the refactor engine so tests are fast,
repeatable, and do not hit the network or require real API keys. The suite covers
the health check, successful JSON requests, successful file uploads, input validation,
and error mapping such as converting a missing OpenAI key into HTTP 503.
"""

from io import BytesIO
from unittest.mock import patch
from app import app as flask_app


def test_health_status() -> None:
    """
    Sanity check that the service is alive and returns the standard payload.
    """
    c = flask_app.test_client()
    r = c.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


@patch("services.ai_client.invoke_refactor_engine",
       return_value={"refactored_code": "X", "explanation": "Y"})
def test_refactor_json_happy(mock_refactor) -> None:
    """
    Verify that JSON requests flow through to the engine and return the expected payload.
    """
    c = flask_app.test_client()
    r = c.post(
        "/api/refactor",
        json={"source": "print(1)", "language": "python", "goals": ["readability"]},
    )
    assert r.status_code == 200
    j = r.get_json()
    assert j["refactored_code"] == "X"
    assert j["explanation"] == "Y"
    # Ensure we passed through the right arguments.
    kwargs = mock_refactor.call_args.kwargs
    assert kwargs["source"] == "print(1)"
    assert kwargs["language"] == "python"
    assert kwargs["goals"] == ["readability"]


def test_refactor_requires_source() -> None:
    """
    Missing 'source' should return a 400 with a helpful message.
    """
    c = flask_app.test_client()
    r = c.post("/api/refactor", json={"language": "python"})
    assert r.status_code == 400
    assert "source" in r.get_json()["error"]


@patch("services.ai_client.invoke_refactor_engine",
       return_value={"refactored_code": "X", "explanation": "Y"})
def test_upload_happy(mock_refactor) -> None:
    """
    Verify that multipart uploads are accepted and passed to the engine, returning
    filename and results.
    """
    c = flask_app.test_client()
    data = {
        "file": (BytesIO(b"console.log('hi');\n"), "hello.js"),
        "language": "javascript",
    }
    r = c.post("/api/upload", data=data, content_type="multipart/form-data")
    assert r.status_code == 200
    j = r.get_json()
    assert j["filename"] == "hello.js"
    assert j["refactored_code"] == "X"
    mock_refactor.assert_called_once()


def test_upload_missing_file() -> None:
    """
    Missing 'file' should return a 400 with a clear error.
    """
    c = flask_app.test_client()
    r = c.post("/api/upload", data={}, content_type="multipart/form-data")
    assert r.status_code == 400


@patch("services.ai_client.invoke_refactor_engine",
       side_effect=RuntimeError("OPENAI_API_KEY is required for refactoring"))
def test_refactor_maps_missing_key_to_503(_mock_engine) -> None:
    """
    When the engine raises a missing-key error, the route should translate it to HTTP 503.
    """
    c = flask_app.test_client()
    r = c.post("/api/refactor", json={"source": "x", "language": "python"})
    assert r.status_code == 503
    j = r.get_json()
    assert "refactor failed" in j["error"]
    assert "OPENAI_API_KEY" in j["detail"]
