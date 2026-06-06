# 🎯 InterviewPilot

> AI-powered mock interview platform with real-time feedback, voice interaction, and session history.

---

## 🚀 What it does

InterviewPilot simulates real job interviews using AI. You talk, it listens, evaluates your answers, and gives you honest feedback — so you stop fumbling in actual interviews.

**Key features:**
- 🎤 Voice recording with speech-to-text (Groq Whisper)
- 📹 Webcam feed for realistic interview simulation
- 🤖 AI interviewer powered by LangGraph + Groq LLMs
- 💬 Real-time per-answer feedback
- 📊 Session history to track your progress
- 🔊 Text-to-speech responses via edge-tts

---

## 🛠️ Tech Stack

| Layer | Tech |
|-------|------|
| AI Orchestration | LangGraph (StateGraph with interrupt/resume) |
| LLM | Groq (Llama 3) |
| STT | Groq Whisper |
| TTS | edge-tts |
| Backend | FastAPI |
| Frontend | React (CDN) |

---

## 📁 Project Structure

```
interviewpilot/
├── server.py 
|__ Backend/             # FastAPI backend — API routes & session management
|      ├── graph/
│      |    ├── workflow.py        # LangGraph StateGraph definition
│      |    ├── node.py           # Graph nodes (question, evaluate, feedback)
|      |    └── schema.py           # Interview state schema
|      ├── utils/
│      |    ├── speech_to_text.py             # Groq Whisper speech-to-text
│      |    ├── text_to_speech.py             # edge-tts text-to-speech
│      |    └── _init_.py      
|      ├──config/
|      |    ├──settings.py
|      |    └── voice.py
|      └──history/
|          └── manager.py
|      
├── static/
│   └── index.html         # React frontend (single-file CDN build)
├──interview_history.json
└── requirements.txt
```

---

## ⚡ Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/interviewpilot.git
cd interviewpilot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run the server

```bash
uvicorn server:app --reload
```

### 5. Open the app

Visit `http://localhost:8000` in your browser.

---

## 🔄 How It Works

```
User speaks → Whisper transcribes → LangGraph processes →
Groq LLM generates question/feedback → edge-tts speaks back → repeat
```

The interview flow is managed by a **LangGraph StateGraph** using interrupt/resume — the graph pauses after each question, waits for your answer, then resumes to evaluate and move forward.

---

## 🧠 LangGraph Flow

```
[Start] → [Generate Question] → [Interrupt: Wait for Answer]
        → [Transcribe Audio] → [Evaluate Answer]
        → [Give Feedback] → [Next Question or End]
```

---

## 📌 Roadmap

- [ ] Role-specific question sets (SDE, Data Analyst, PM, etc.)
- [ ] Scoring dashboard with charts
- [ ] Resume-based question generation
- [ ] Cloud deployment (Render / Railway)
- [ ] User auth + persistent session history

---

## 🙋 Author

**Bhoomi**  
Final-year BCA student | AI Engineer  


---

## 📄 License

MIT License — feel free to use, modify, and build on this.