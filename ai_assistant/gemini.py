"""
Shared Gemini client for the Mind Nest project.

Import `gemini_client` from here instead of initialising a new
genai.Client() in each app. This avoids circular imports and ensures
only one client instance exists across the whole project.
"""
import os
from dotenv import load_dotenv

load_dotenv()

_api_key = os.getenv('AI_API_KEY', '')

if _api_key:
    from google import genai
    gemini_client = genai.Client(api_key=_api_key)
else:
    gemini_client = None
