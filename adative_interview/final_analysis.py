from adative_interview.state import InterviewState
import json
import re

from langchain_ollama import ChatOllama

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

    # trailing comma hatao
    content = re.sub(r",\s*([}\]])", r"\1", content)

    return json.loads(content, strict=False)


def to_list(value):
    if isinstance(value, list):
        return [str(v) for v in value]
    if value:
        return [str(value)]
    return []


def final_analysis(state: InterviewState):

    full_history = state.get("interview_history", [])

    # Pehli entry intro ki hai, usko analysis se hata do
    technical_history = full_history[1:] if len(full_history) > 1 else full_history

    # Overall score code se nikalo: sab technical answers ka average
    scores = [h.get("score", 0) for h in technical_history if isinstance(h.get("score"), (int, float))]
    overall_score = round(sum(scores) / len(scores)) if scores else 0

    # Model ko sirf kaam ki cheezein do, bhari hui history nahi
    summary_lines = []
    for i, h in enumerate(technical_history, start=1):
        summary_lines.append(
            f"Q{i}: {h.get('question', '')}\n"
            f"Answer: {h.get('answer', '')}\n"
            f"Score: {h.get('score', '')}/10\n"
            f"Missing points: {h.get('missing_points', [])}\n"
        )
    history_text = "\n".join(summary_lines)

    prompt = f"""
You are an AI candidate assessment analyst.

Below are the candidate's technical interview answers with scores.

{history_text}

Rules:
1. Base the analysis ONLY on the answers above.
2. Do not invent skills or knowledge that the candidate did not demonstrate.
3. Use each technology only for what the candidate actually said it was used for.
4. Do not repeat the same point in different words.
5. strengths: maximum 4 short items.
6. weaknesses: maximum 4 short items, each about a different topic.
7. skills_demonstrated: only technologies the candidate explained in an answer.
8. skill_gaps: maximum 3 short items.
9. improvement_plan: maximum 4 practical items.
10. Every item must be a short plain-text string.

Return ONLY a JSON object in this exact format:

{{
    "strengths": ["..."],
    "weaknesses": ["..."],
    "skills_demonstrated": ["..."],
    "skill_gaps": ["..."],
    "improvement_plan": ["..."]
}}
"""

    try:
        response = llm.invoke(prompt)
        print("\n========== FINAL ANALYSIS RAW RESPONSE ==========")
        print(response.content)
        print("=================================================")
        data = safe_json_loads(response.content)
    except Exception as e:
        print("FINAL ANALYSIS JSON FAILED:", e)
        data = {}

    result = {
        "overall_score": overall_score,
        "strengths": to_list(data.get("strengths")),
        "weaknesses": to_list(data.get("weaknesses")),
        "skills_demonstrated": to_list(data.get("skills_demonstrated")),
        "skill_gaps": to_list(data.get("skill_gaps")),
        "improvement_plan": to_list(data.get("improvement_plan")),
    }

    return {
        "final_analysis": result,
        "current_question": ""
    }