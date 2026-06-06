import json
import os
import datetime
HISTORY_FILE = "interview_history.json"


def _load_raw() -> dict:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_raw(data: dict) -> None:
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def history_start_session(thread_id: str, role: str, difficulty: str, max_q: int) -> None:
    """Create a new session entry in history."""
    data = _load_raw()
    data[thread_id] = {
        "thread_id":  thread_id,
        "role":       role,
        "difficulty": difficulty,
        "max_question": max_q,
        "started_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "completed":  False,
        "qa_pairs":   [],          # list of {question, answer, feedback}
    }
    _save_raw(data)


def history_add_qa(thread_id: str, question: str, answer: str, feedback: str) -> None:
    """Append a Q/A/Feedback triple to an existing session."""
    data = _load_raw()
    if thread_id not in data:
        return
    data[thread_id]["qa_pairs"].append({
        "question": question,
        "answer":   answer,
        "feedback": feedback,
    })
    _save_raw(data)


def history_mark_complete(thread_id: str) -> None:
    data = _load_raw()
    if thread_id in data:
        data[thread_id]["completed"] = True
        data[thread_id]["finished_at"] = datetime.datetime.now().isoformat(timespec="seconds")
    _save_raw(data)


def history_get_all() -> list[dict]:
    """Return all sessions newest-first."""
    data = _load_raw()
    sessions = list(data.values())
    sessions.sort(key=lambda s: s.get("started_at", ""), reverse=True)
    return sessions


def history_get_session(thread_id: str) -> dict | None:
    return _load_raw().get(thread_id)