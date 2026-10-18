from adative_interview.state import InterviewState
from langgraph.types import interrupt


def candidate_answer(state: InterviewState):

    answer = interrupt("Please provide your answer")

    return {
        "candidate_answer": answer
    }