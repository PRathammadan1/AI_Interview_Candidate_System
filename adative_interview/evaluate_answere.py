from dotenv import load_dotenv
from adative_interview.state import InterviewState

import json
import re
from langchain_ollama import ChatOllama

load_dotenv()

llm = ChatOllama(
    model="gemma3:4b",
    temperature=0,
    format="json",
    think=False
)


def safe_json_loads(content: str) -> dict:
    content = content.replace("```json", "").replace("```", "").strip()
    start, end = content.find("{"), content.rfind("}") + 1
    content = content[start:end]

    # trailing comma hatao: {"a": 1,} -> {"a": 1}
    content = re.sub(r",\s*([}\]])", r"\1", content)

    # strict=False: string ke andar asli Enter/tab ho to bhi chalega
    return json.loads(content, strict=False)


def to_list(value):
    if isinstance(value, list):
        return [str(v) for v in value]
    if value:
        return [str(value)]
    return []


def evaluate_answer(state: InterviewState):

    question = state["current_question"]
    answer = state["candidate_answer"]
    question_count = state["question_count"]

    # Intro ka answer score nahi karte, warna difficulty shuru se hi bigad jati hai
    if question_count == 0:
        result = {
            "score": 5,
            "strengths": [],
            "missing_points": [],
            "feedback": "Introduction received.",
        }
    else:
        prompt = f"""
You are a strict but fair technical interviewer.

Evaluate the candidate's answer ONLY against the question asked.

Question:
{question}

Candidate Answer:
{answer}

Rules:
1. Evaluate only what the candidate actually said.
2. Do not give credit for information that the candidate did not mention.
3. Do not assume that the candidate knows something just because it is
   related to the project or technology.
4. Do not invent missing details.
5. Give a score from 1 to 10.
6. Score based on correctness, relevance, clarity, and completeness.
7. Keep the evaluation concise and factual.
8. strengths and missing_points must be short plain-text strings.
9. feedback must be ONE or TWO plain sentences. Do not use quotes or asterisks inside it.

Return ONLY a JSON object in this exact format:

{{
    "score": 5,
    "strengths": ["point 1"],
    "missing_points": ["point 1"],
    "feedback": "short feedback here"
}}
"""

        response = llm.invoke(prompt)

        print("OLLAMA EVALUATION RESPONSE:")
        print(response.content)

        try:
            result = safe_json_loads(response.content)
        except Exception as e:
            print("EVALUATION JSON FAILED:", e)
            result = {
                "score": 5,
                "strengths": [],
                "missing_points": [],
                "feedback": "Could not evaluate this answer properly.",
            }

    # Score ko hamesha 1-10 ke beech ka integer banao
    try:
        score = int(float(result.get("score", 5)))
    except (TypeError, ValueError):
        score = 5
    score = max(1, min(10, score))

    strengths = to_list(result.get("strengths"))
    missing_points = to_list(result.get("missing_points"))

    feedback = str(result.get("feedback", "")).strip()
    if not feedback:
        feedback = "Answer evaluated."

    history_entry = {
        "question": question,
        "answer": answer,
        "score": score,
        "strengths": strengths,
        "missing_points": missing_points,
        "feedback": feedback,
        "difficulty": state.get("difficulty", "normal"),
    }

    # Purani list ko badalne ki jagah nayi list banao
    interview_history = list(state.get("interview_history", []))
    interview_history.append(history_entry)

    return {
        "score": score,
        "strengths": strengths,
        "missing_points": missing_points,
        "feedback": feedback,
        "question_count": question_count + 1,
        "interview_history": interview_history,
    }


if __name__ == "__main__":

    state = {
        "current_question": "Could you explain how you implemented RAG in your AI-powered productivity chatbot?",
        "candidate_answer": "",
        "score": 0,
        "question_count": 2,
        "strengths": [],
        "missing_points": [],
        "feedback": "",
        "difficulty": "normal",
        "interview_history": []
    }

    answer = input("Your Answer: ")
    state["candidate_answer"] = answer

    result = evaluate_answer(state)

    print("\nEvaluation:")
    print("Score:", result["score"])
    print("Strengths:", result["strengths"])
    print("Missing Points:", result["missing_points"])
    print("Feedback:", result["feedback"])