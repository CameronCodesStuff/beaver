import os
import re
import json
import urllib.request

from core import config

API_URL = "https://api.anthropic.com/v1/messages"

SYSTEM = (
    "You are a web generator. Output a single, complete, self-contained HTML "
    "document (HTML, CSS, and JS all inline in one file). No explanations, no "
    "markdown fences — return only the raw HTML starting with <!DOCTYPE html>. "
    "Make it visually polished, responsive, and fully functional. Use a clean "
    "modern aesthetic with a dark theme unless the user asks otherwise."
)


def get_api_key():
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key
    key_path = os.path.join(config.BASE_DIR, "api_key.txt")
    if os.path.isfile(key_path):
        try:
            with open(key_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return None


def has_api_key():
    return bool(get_api_key())


def _call(messages):
    key = get_api_key()
    if not key:
        raise RuntimeError("no_api_key")
    body = json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 8000,
        "system": SYSTEM,
        "messages": messages,
    }).encode("utf-8")
    req = urllib.request.Request(
        API_URL, data=body, method="POST",
        headers={
            "Content-Type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read().decode("utf-8"))
    parts = [b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]
    return "".join(parts)


def _clean_html(text):
    text = text.strip()
    text = re.sub(r"^```(?:html)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    m = re.search(r"<!DOCTYPE html.*?</html>", text, re.S | re.I)
    if m:
        return m.group(0)
    m = re.search(r"<html.*?</html>", text, re.S | re.I)
    return m.group(0) if m else text


def generate(prompt, history=None):
    """Generate or revise a site. history = prior [{role, content}] messages.
    Returns (html, updated_history) or (None, error_string)."""
    messages = list(history or [])
    messages.append({"role": "user", "content": prompt})
    try:
        raw = _call(messages)
    except RuntimeError:
        return None, "no_api_key"
    except Exception as e:
        return None, f"Generation failed: {e}"

    html = _clean_html(raw)
    if "<" not in html:
        return None, "The generator didn't return valid HTML."

    messages.append({"role": "assistant", "content": html})
    return html, messages


def save(html, name="site"):
    os.makedirs(config.SITES_DIR, exist_ok=True)
    safe = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")[:40] or "site"
    path = os.path.join(config.SITES_DIR, f"{safe}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path
