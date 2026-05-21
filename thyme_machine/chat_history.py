"""
Persistent chat history — saved to data/chat_history.json between sessions.
"""

import json
from pathlib import Path

_HISTORY_PATH = Path("./data/chat_history.json")
_MAX_SAVED_TURNS = 50  # keep last 50 turns on disk


def load_chat_history() -> list[dict]:
    if _HISTORY_PATH.exists():
        try:
            return json.loads(_HISTORY_PATH.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_chat_history(history: list[dict]) -> None:
    _HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    _HISTORY_PATH.write_text(
        json.dumps(history[-_MAX_SAVED_TURNS:], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def clear_chat_history() -> None:
    st_history_path = _HISTORY_PATH
    if st_history_path.exists():
        st_history_path.unlink()
