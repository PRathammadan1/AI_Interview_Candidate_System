from adative_interview.state import InterviewState


def route_question(state: InterviewState):

    question_count = state["question_count"]

    # Interview complete
    if question_count >= 10:
        return "end"


    score = state["score"]

    if score < 5:
        return "weak"

    elif score < 8:
        return "medium"

    else:
        return "strong"



if __name__ == "__main__":
    
    state = {
        "score": 10,
        "question_count": 5
    }

    result = route_question(state)

    print("Route:", result)