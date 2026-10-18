from typing import TypedDict, List, Dict, Any


class InterviewState(TypedDict, total=False):
    # candidate info
    name: str

    # current question aur answer
    current_question: str
    candidate_answer: str
    transition_message: str      # acknowledgement ("Okay, got it...")

    # evaluation
    score: int
    strengths: List[str]
    missing_points: List[str]
    feedback: str

    # interview flow
    difficulty: str              # "easy" / "normal" / "hard"
    question_count: int
    interview_history: List[Dict[str, Any]]
    total_questions : int
    # resume se nikale hue topics
    topics: Dict[str, List[str]]  # {"projects": [...], "skills": [...]}
    plan: dict

    # end mein final report
    final_analysis: Dict[str, Any]