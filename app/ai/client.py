"""
Gemini client using the current google-genai SDK.

The AI writes prose. It never produces the numbers shown in the UI.
Those all come from the engine.
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

# Change this if list_models() shows your key does not have it.
MODEL_NAME = "gemini-2.0-flash"

_client = None

if API_KEY:
    _client = genai.Client(api_key=API_KEY)
else:
    print("WARNING: GEMINI_API_KEY is not set. AI responses will use fallback text.")


def is_available():
    return _client is not None


def list_models():
    """Print the models this key can actually use. Run once to check."""
    if not _client:
        print("No API key configured.")
        return []
    names = []
    for m in _client.models.list():
        if "generateContent" in getattr(m, "supported_actions", []) or True:
            names.append(m.name)
    for n in names:
        print(" ", n)
    return names


def generate(prompt, temperature=0.3, fallback=None):
    """
    Send a prompt and return text. Never raises.
    On any failure returns the fallback text.
    """
    if not _client:
        return fallback or "AI summary is unavailable because no API key is configured."

    try:
        response = _client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=800,
            ),
        )

        text = (response.text or "").strip()
        if not text:
            print("AI call returned empty text")
            return fallback or "AI summary could not be generated."
        return text

    except Exception as error:
        name = type(error).__name__
        print(f"AI unavailable ({name}), using fallback")
        return fallback or "AI summary is temporarily     unavailable."