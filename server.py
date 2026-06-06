"""
server.py – FastAPI wrapper around history_back.py
Run: uvicorn server:app --reload --port 8000
"""
import uuid
import base64
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langgraph.errors import GraphInterrupt
from langgraph.types import Command

# ── Import everything from your existing backend ──────────────────────────────

from backend.graph.workflow import workflow         
from  backend.history.manager import (
    history_start_session,
    history_add_qa,
    history_mark_complete,
    history_get_all,
    history_get_session,
)

from  backend.utils.text_to_speech import text_to_speech_bytes
from backend.utils.speech_to_text import speech_to_text_bytes
from  backend.config.voice import INTERVIEWER_VOICE,FEEDBACK_VOICE

app = FastAPI(title="InterviewPilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _sync_state(thread_id: str) -> dict:
    """Pull latest state + interrupt payload from graph."""
    config = {"configurable": {"thread_id": thread_id}}
    gs = workflow.get_state(config)
    state = dict(gs.values) if gs and gs.values else {}

    # Grab question from interrupt payload if present
    try:
        payload = gs.tasks[0].interrupts[0].value
        if isinstance(payload, dict) and "question" in payload:
            state["question"] = payload["question"]
    except (IndexError, AttributeError):
        pass

    # Pull latest feedback from history if not in current state
    if not state.get("feedback"):
        try:
            for snap in workflow.get_state_history(config):
                fb = snap.values.get("feedback")
                if fb:
                    state["feedback"] = fb
                    state.setdefault("_last_question", snap.values.get("question", ""))
                    state.setdefault("_last_answer",   snap.values.get("answer", ""))
                    break
        except Exception:
            pass

    return state


def _graph_done(thread_id: str) -> bool:
    gs = workflow.get_state({"configurable": {"thread_id": thread_id}})
    return gs is not None and len(gs.next) == 0


def _audio_b64(text: str, voice: str) -> str | None:
    try:
        raw = text_to_speech_bytes(text, voice)
        return base64.b64encode(raw).decode()
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════════════
# Routes
# ══════════════════════════════════════════════════════════════════════════════

class StartBody(BaseModel):
    role: str
    difficulty: str
    max_question: int


@app.post("/start")
def start_interview(body: StartBody):
    """Create a new interview session, generate first question + audio."""
    tid = str(uuid.uuid4())

    initial_state = {
        "role":            body.role,
        "difficulty":      body.difficulty,
        "max_question":    body.max_question,
        "question_number": 0,
        "question":        "",
        "answer":          "",
        "feedback":        None,
    }

    history_start_session(tid, body.role, body.difficulty, body.max_question)

    try:
        workflow.invoke(
            initial_state,
            config={"configurable": {"thread_id": tid}},
        )
    except GraphInterrupt:
        pass

    state = _sync_state(tid)
    question = state.get("question", "")
    q_audio  = _audio_b64(question, INTERVIEWER_VOICE) if question else None

    return {
        "thread_id":       tid,
        "question":        question,
        "question_number": state.get("question_number", 1),
        "max_question":    body.max_question,
        "question_audio":  q_audio,
    }


class AnswerBody(BaseModel):
    thread_id: str
    answer: str


@app.post("/answer")
def submit_answer(body: AnswerBody):
    """Resume the graph with an answer; return feedback + next question."""
    tid = body.thread_id

    try:
        workflow.invoke(
            Command(resume=body.answer),
            config={"configurable": {"thread_id": tid}},
        )
    except GraphInterrupt:
        pass

    state    = _sync_state(tid)
    done     = _graph_done(tid)
    feedback = state.get("feedback", "")

    # Persist Q/A/Feedback
    question_just_answered = state.get("_last_question") or state.get("question", "")
    history_add_qa(tid, question_just_answered, body.answer, feedback)

    fb_audio = _audio_b64(feedback, FEEDBACK_VOICE) if feedback else None

    if done:
        history_mark_complete(tid)
        return {
            "done":     True,
            "feedback": feedback,
            "fb_audio": fb_audio,
        }

    next_question = state.get("question", "")
    q_audio       = _audio_b64(next_question, INTERVIEWER_VOICE) if next_question else None

    return {
        "done":            False,
        "feedback":        feedback,
        "fb_audio":        fb_audio,
        "question":        next_question,
        "question_number": state.get("question_number", 0),
        "question_audio":  q_audio,
    }


class TranscribeBody(BaseModel):
    audio_b64: str   # base64-encoded webm/wav blob from browser


@app.post("/transcribe")
def transcribe(body: TranscribeBody):
    raw = base64.b64decode(body.audio_b64)
    try:
        text = speech_to_text_bytes(raw)
        return {"transcript": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
def get_history():
    return history_get_all()


@app.get("/history/{thread_id}")
def get_session(thread_id: str):
    session = history_get_session(thread_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session