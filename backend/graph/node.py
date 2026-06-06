from backend.graph.schema import chatschema
from langchain_core.messages import SystemMessage,HumanMessage
from langgraph.types import interrupt
from backend.config.settings import model
# ── Nodes ─────────────────────────────────────────────────────────────────────
def generate_question(state: chatschema) -> chatschema:
    # Defensive: ensure 'role' is present (handles edge cases on resume)
    role       = state.get("role", "Software Engineer")
    difficulty = state.get("difficulty", "Intermediate")
    q_num      = state.get("question_number", 0)
    max_q      = state.get("max_question", 5)

    messages = [
        SystemMessage(
            content=(
                f"You are a professional technical interviewer for the role of {role}.\n"
                f"Ask a clear, concise interview question with difficulty level: {difficulty}.\n"
                f"This is question {q_num + 1} of {max_q}.\n"
                "- Do NOT repeat previous questions.\n"
                "- Ask ONLY the question text, nothing else."
            )
        )
    ]
    result = model.invoke(messages)
    return {
        **state,
        "question":        result.content.strip(),
        "question_number": q_num + 1,
        "feedback":        None,
        "answer":          "",
    }


def collect_answer(state: chatschema) -> chatschema:
    """Pause — Streamlit resumes with Command(resume=<answer_text>)."""
    answer = interrupt({"question": state["question"]})
    return {**state, "answer": answer}


def evaluate_answer(state: chatschema) -> chatschema:
    role = state.get("role", "Software Engineer")
    messages = [
        SystemMessage(
            content=(
                f"You are a senior technical interviewer evaluating a candidate for {role}.\n"
            "Give structured feedback in exactly this format:\n\n"
            "Strengths: [what the candidate did well]\n"
            "Areas to improve: [specific gaps or missing points]\n"
            "Tip: [one actionable advice for next time]\n"
            "Score: [X/10]\n\n"
            "Keep it concise, honest, and encouraging. 4-6 sentences max."
            )
        ),
        HumanMessage(
            content=f"Question: {state['question']}\n\nAnswer: {state['answer']}"
        ),
    ]
    result = model.invoke(messages)
    return {**state, "feedback": result.content.strip()}


def check_before_generate(state: chatschema):
    if state.get("question_number", 0) >= state.get("max_question", 5):
        return "end"
    return "generate_question"
