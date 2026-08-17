import os
from pathlib import Path


# ─── LLM / OpenRouter Config ─────────────────────────────────────────────────
OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    ""
)

OPENROUTER_API_URL = os.getenv(
    "OPENROUTER_API_URL",
    "https://openrouter.ai/api/v1/chat/completions"
)