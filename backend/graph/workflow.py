from langgraph.graph import StateGraph,END
from backend.graph.node import generate_question,collect_answer,evaluate_answer,check_before_generate
from backend.graph.schema import chatschema
from backend.config.settings import checkpointer
# ── Graph ─────────────────────────────────────────────────────────────────────

graph = StateGraph(chatschema)

graph.add_node("generate_question", generate_question)
graph.add_node("collect_answer",    collect_answer)
graph.add_node("evaluate_answer",   evaluate_answer)

graph.set_entry_point("generate_question")
graph.add_edge("generate_question", "collect_answer")
graph.add_edge("collect_answer",    "evaluate_answer")
graph.add_conditional_edges(
    "evaluate_answer",
    check_before_generate,
    {"generate_question": "generate_question", "end": END},
)
workflow = graph.compile(checkpointer=checkpointer)
