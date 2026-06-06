from typing import TypedDict,Optional
# ── State schema ──────────────────────────────────────────────────────────────
class chatschema(TypedDict):
    role:            str
    question_number: int
    max_question:    int
    difficulty:      str
    question:        str
    answer:          str
    feedback:        Optional[str]

