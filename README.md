# Jawab Interview: Adaptive, Resume-Grounded Interview Practice

An AI interview practice system that reads your resume, asks technical questions about **your own** projects and skills, and adjusts the difficulty of each question to the quality of your previous answer. At the end it gives you a report with your strengths, gaps and an improvement plan.

It runs fully on your own computer with a small open model (Gemma 3, 4B) served by Ollama. No paid API is needed.

> **Status:** working prototype. Manual testing and one expert review are done. A student pilot is still pending, so no accuracy claims are made.

## Why this project

Most interview practice uses generic question lists, but a real interviewer usually asks about what is written on your resume. A small language model used on its own also repeats topics, asks shallow questions and sometimes assumes things the resume does not say. This project controls the interview structure in code and uses the model for wording, evaluation and extraction.

## Features

- Resume upload (PDF or DOCX), parsed and indexed with FAISS (RAG)
- Automatic extraction of projects, skills and internships
- Fixed interview structure with technical questions built from core concepts of your resume keywords
- Answer scoring from 1 to 10 with strengths, missing points and feedback
- Adaptive difficulty: weak answer gives an easier next question, strong answer gives a harder one
- Final assessment report (overall score is computed in code)
- Chat-style web interface with progress bar and difficulty indicator
- Full mode (10 questions) and quick mode (5 questions)

## How it works

```
Resume (PDF/DOCX)
   -> parse -> split into chunks -> embeddings -> FAISS index
   -> topic extraction (projects, skills, internships)

Interview loop (LangGraph state machine)
   ask question -> wait for answer -> evaluate (score 1-10)
        -> router -> easy / normal / hard question -> ...
   -> final analysis report
```

### Interview structure (full mode, 10 questions)

| Question | Type | Source |
|---|---|---|
| 1 | Introduction | Fixed |
| 2 | Project | A project from the resume |
| 3, 5, 7 | Keyword concept | A core concept of a resume skill (for example OOP or multithreading for Java) |
| 4, 6, 8, 9 | Open technical | Resume skills, often short problem scenarios |
| 10 | Internship or experience | Role, learning and one challenge |

The introduction answer is not scored, so the interview always starts at normal difficulty.

## Tech stack

| Part | Technology |
|---|---|
| Backend | Python, FastAPI |
| Orchestration | LangChain, LangGraph |
| Retrieval | FAISS, embeddings through Ollama |
| Language model | Gemma 3 (4B) served by Ollama |
| Frontend | HTML, CSS, JavaScript (single page) |

## Project structure

```
backend/              FastAPI app, resume parsing, chunking, embeddings, FAISS search, topic extraction
adative_interview/    LangGraph graph, state, router, question generators, evaluation, final analysis
frontend/             Single-page chat interface (index.html)
docs/                 Uploaded resumes (created locally, not committed)
faiss_index/          Saved index and chunks (created locally, not committed)
```

## Getting started

### 1. Requirements

- Python 3.11
- [Ollama](https://ollama.com/) installed and running
- About 8 GB RAM is enough for the 4B model

### 2. Install

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
mkdir docs faiss_index
```

### 3. Pull the models

```bash
ollama pull gemma3:4b
ollama pull <embedding-model>   # the embedding model used in backend/embedding.py
```

### 4. Run

```bash
uvicorn backend.uploads:app
```

Open http://localhost:8000 in your browser, upload a resume, enter your name and start the interview.

Run without `--reload`. The upload step writes files inside the project folder, and auto-reload can restart the server in the middle of an interview.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Serves the web interface |
| POST | `/upload` | Uploads a resume, builds the FAISS index |
| POST | `/interview/start` | Starts an interview, returns the first question |
| POST | `/interview/answer` | Submits an answer, returns the next question, score, feedback and (at the end) the final report |

## Known limitations

- Interview state is kept in memory, so it is lost when the server restarts.
- All users share one resume index, so only one interview can run at a time.
- Text answers only. No voice input, login or integrity monitoring yet.
- A 4B model can still produce weak or inaccurate questions and scores. Scores are indicative, not exact.
- The question bank covers a few skills. Skills outside the bank use model-generated questions, which are unverified.
- This is a **practice tool**. It must not be used to make hiring decisions, or to get answers during a live interview.

## Roadmap

- [ ] Student pilot study (completion rate, question relevance, score reliability)
- [ ] Per-user resume index and persistent storage
- [ ] Login and user accounts
- [ ] Job-description-based interview mode and practice mode
- [ ] Voice input
- [ ] Wider verified question bank
- [ ] Comparison of the 4B model with larger models for scoring

## Privacy

A resume contains personal data. Use sample resumes while testing. The `docs/` and `faiss_index/` folders are ignored by Git and must never be committed. Delete uploaded files when you are done.

## Author

**Pratham Madan**, B.Tech (Computer Science and Engineering), Galgotias University
[LinkedIn / email: add here]

## License

[Choose a license, for example MIT, and add a LICENSE file]
