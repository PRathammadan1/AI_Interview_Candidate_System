
# AI Interview Candidate System

An AI-powered adaptive interview and candidate assessment system that generates resume-based technical questions, evaluates candidate answers, and adjusts interview difficulty according to performance.

## Overview

Traditional interview preparation often relies on generic questions that may not reflect a candidate's actual skills or project experience.

This project aims to make interview practice more personalized by combining resume-based retrieval, large language models, structured question generation, and adaptive difficulty selection.

The system is designed as an interview practice and assessment tool, helping candidates identify technical knowledge gaps and improve their interview performance.

## Key Features

- **Resume-Based Question Generation:** Generates interview questions using information extracted from a candidate's resume.
- **Retrieval-Augmented Generation (RAG):** Retrieves relevant resume content to provide context for question generation.
- **Semantic Search:** Uses embeddings and FAISS for similarity-based retrieval of relevant text chunks.
- **Adaptive Interviewing:** Adjusts question difficulty based on candidate performance.
- **Answer Evaluation:** Analyzes candidate answers using AI-based evaluation.
- **Structured Interview Flow:** Organizes question generation and answer evaluation into separate modules.
- **Final Assessment:** Includes a module for analyzing interview performance.

## System Workflow

1. Upload a candidate's resume.
2. Extract and split resume text into smaller chunks.
3. Generate embeddings and store them in a FAISS index.
4. Retrieve relevant resume information for a selected topic.
5. Generate an interview question based on the retrieved context.
6. Evaluate the candidate's answer.
7. Select the next question difficulty based on performance.
8. Generate a final assessment of the interview.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend API | FastAPI |
| Language Model Runtime | Ollama |
| Language Model | Gemma 3 4B |
| Retrieval Approach | Retrieval-Augmented Generation (RAG) |
| Vector Search | FAISS |
| Embeddings | Ollama-based embeddings |
| Interview Orchestration | LangGraph |
| Frontend | HTML, CSS, JavaScript |

## Project Structure

```text
AI_Interview_Candidate_System/
│
├── adative_interview/
│   ├── candidate_answere.py
│   ├── evaluate_answere.py
│   ├── final_analysis.py
│   ├── generate_easy_question.py
│   ├── generate_normal_question.py
│   ├── generate_hard_question.py
│   ├── generate_question.py
│   ├── graph.py
│   ├── question_engine_all.py
│   ├── router.py
│   └── state.py
│
├── backend/
│   ├── embedding.py
│   ├── faiss_search.py
│   ├── generation.py
│   ├── parser.py
│   ├── text_splitting.py
│   ├── topic.py
│   └── uploads.py
│
├── frontend/
│   └── index.html
│
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or a compatible version for the installed dependencies
- Git
- Ollama installed and running
- Required Python packages
- The language model and embedding model used by the application

### 1. Clone the Repository

```bash
git clone https://github.com/PRathammadan1/AI_Interview_Candidate_System.git
cd AI_Interview_Candidate_System
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

Install the required packages listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 4. Set Up the Language Model

Make sure Ollama is installed and running. Download the model required by the application if it is not already available.

For example, if the project uses Gemma 3 4B:

```bash
ollama pull gemma3:4b
```

Check the model name in the project configuration before running the application.

### 5. Run the Backend

```bash
uvicorn backend.uploads:app --reload
```

Open the FastAPI documentation:

http://127.0.0.1:8000/docs

### 6. Run the Frontend

Open a separate terminal:

```bash
python -m http.server 5500
```

Then open:

http://127.0.0.1:5500/frontend/

If the frontend or backend uses a different entry point, update the command according to the project configuration.

## Current Scope

The current implementation focuses on resume processing, semantic retrieval, interview question generation, answer evaluation, and adaptive interview logic.

The project is under development. Additional capabilities, integrations, and evaluation improvements may be introduced as development progresses.

## Limitations

- AI-generated questions and scores may not always be accurate.
- Assessment quality depends on the resume content, retrieved context, and model behavior.
- Further testing is needed to evaluate question quality, repetition, and scoring consistency.
- The system is intended to support interview practice and should not be treated as a definitive hiring decision-maker.

## Future Improvements

- Job description and candidate skill matching
- Improved evidence-based scoring and feedback
- Better control over question relevance and repetition
- Candidate skill-gap analysis and personalized practice
- Improved user interface and assessment reports

## Disclaimer

This project is intended for educational, development, and interview-practice purposes. AI-generated assessments should be reviewed critically and should not replace human judgment.

## Author

**Pratham Madan**

GitHub: [@PRathammadan1](https://github.com/PRathammadan1)
