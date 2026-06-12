from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
import os

MODEL_NAME = "llama3-70b-8192"
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY","").strip()
model       = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",   # stronger model → better interview feel
    temperature=1.7,
)
checkpointer = InMemorySaver()
 