from langgraph.graph import StateGraph
from adative_interview.state import InterviewState
from adative_interview.generate_question import generate_question
from adative_interview.candidate_answere import candidate_answer
from adative_interview.generate_easy_question import generate_easy_question
from adative_interview.generate_normal_question import generate_normal_question
from adative_interview.generate_hard_question import generate_hard_question
from adative_interview.evaluate_answere import evaluate_answer
from adative_interview.router import route_question
from adative_interview.final_analysis import final_analysis
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START
from langgraph.graph import END

graph = StateGraph(InterviewState)
graph.add_node("generate_question", generate_question)
graph.add_node("candidate_answer",candidate_answer)
graph.add_node("generate_easy_question" ,generate_easy_question)
graph.add_node("generate_normal_question" ,generate_normal_question)
graph.add_node("generate_hard_question" ,generate_hard_question)
graph.add_node("evaluate_answer", evaluate_answer)
graph.add_node("final_analysis", final_analysis)


graph.add_edge(START, "generate_question")
graph.add_edge("generate_question", "candidate_answer")
graph.add_edge("candidate_answer" , "evaluate_answer")

graph.add_conditional_edges(
    "evaluate_answer",
    route_question,
    {
        "weak": "generate_easy_question",
        "medium": "generate_normal_question",
        "strong": "generate_hard_question",
        "end": "final_analysis"
    }
)

graph.add_edge("generate_easy_question", "candidate_answer")
graph.add_edge("generate_normal_question", "candidate_answer")
graph.add_edge("generate_hard_question", "candidate_answer")
graph.add_edge("final_analysis", END)

checkpointer = InMemorySaver()

compiled_graph = graph.compile(
    checkpointer=checkpointer
)


# initial_state = {
#     "current_question": "",
#     "candidate_answer": "",
#     "score": 0,
#     "strengths": [],
#     "missing_points": [],
#     "feedback": "",
#     "difficulty": "normal",
#     "interview_history": [],
#     "question_count": 0,
#     "final_analysis": {}
# }

# result = compiled_graph.invoke(initial_state)

# print(result)