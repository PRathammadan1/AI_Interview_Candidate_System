from adative_interview.state import InterviewState
from .question_engine_all import build_question

def generate_hard_question(state: InterviewState):
    return build_question(state, "hard")