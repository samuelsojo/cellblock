"""Minimal OpenAI-compatible chat client. Works with Ollama (local) or any API.

Config via environment (or a .env file next to this one):
  CELLBLOCK_BASE_URL  default http://localhost:11434/v1  (Ollama)
  CELLBLOCK_MODEL     default llama3
  CELLBLOCK_API_KEY   default "ollama" (Ollama ignores it)
"""
import json
import os
import urllib.request
from pathlib import Path


def _load_dotenv():
    env = Path(__file__).with_name(".env")
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()
BASE_URL = os.environ.get("CELLBLOCK_BASE_URL", "http://localhost:11434/v1").rstrip("/")
MODEL = os.environ.get("CELLBLOCK_MODEL", "llama3")
API_KEY = os.environ.get("CELLBLOCK_API_KEY", "ollama")


def chat(messages, temperature=0.7):
    """Send a list of {role, content} messages, return the assistant's reply text."""
    body = json.dumps({"model": MODEL, "messages": messages, "temperature": temperature}).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)["choices"][0]["message"]["content"]
