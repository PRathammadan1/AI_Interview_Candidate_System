from fastapi import FastAPI , UploadFile , File
from backend.parser import extract_text
from backend.text_splitting import split_text
from backend.embedding import create_embedding
from backend.faiss_search import create_faiss_index
from backend.retrivel import retrieve, reload_index
from backend.argumentes import create_prompt
from backend.generation import generate_answer
from backend.evalution import evaluate_answer
from pydantic import BaseModel
from adative_interview.state import InterviewState
from adative_interview.graph import compiled_graph
import uuid
from langgraph.types import Command
from backend.topic import extract_topics
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse


import pickle
import faiss

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return FileResponse("frontend/index.html")

class InterviewStartRequest(BaseModel):
    name: str

class InterviewAnswerRequest(BaseModel):
    interview_id: str
    answer: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
        # this is a file path 
        file_path = f"docs/{file.filename}"
       
        data = await file.read()

        with open(file_path, "wb") as f:
           f.write(data)

        text = extract_text(file_path)
        print("TEXT LENGTH:", len(text))
        chunk = split_text(text)
        # Chunks ko save karo
        with open("faiss_index/chunks.pkl", "wb") as f:
         pickle.dump(chunk, f)

       
        print("Chunks saved:", len(chunk))
        print("First chunk:", chunk[0])

        vector = create_embedding(chunk)

        store = create_faiss_index(vector)

        faiss.write_index(store, "faiss_index/index.faiss")

        reload_index()   # naya resume memory mein load ho jayega

        return {
            "filename": file.filename,
            "chunks": len(chunk),
            "status": "uploaded"
        }

@app.post("/interview/start")
async def start_interview(request: InterviewStartRequest):

    name = request.name

    interview_id = str(uuid.uuid4())

    initial_state: InterviewState = {
        "name": name,
        "current_question": "",
        "candidate_answer": "",
        "score": 0,
        "strengths": [],
        "missing_points": [],
        "feedback": "",
        "difficulty": "normal",
        "interview_history": [],
        "question_count": 0,
         "total_questions": 10,
        "topics": extract_topics(), 
        "final_analysis": {}
    }

    config = {
        "configurable": {
            "thread_id": interview_id
        }
    }

    result = compiled_graph.invoke(
        initial_state,
        config
    )

    return {
        "interview_id": interview_id,
        "message": f"Hi {name}, let's begin your interview.",
        "question": result["current_question"]
    }

@app.post("/interview/answer")
async def submit_answer(request: InterviewAnswerRequest):

    config = {
        "configurable": {
            "thread_id": request.interview_id
        }
    }
    snapshot_before = compiled_graph.get_state(config)

    print("========== BEFORE RESUME ==========")
    print("NEXT:", snapshot_before.next)
    print("VALUES:", snapshot_before.values)
    print("TASKS:", snapshot_before.tasks)
    print("===================================")

    
    result = compiled_graph.invoke(
        Command(resume=request.answer),
        config
    )

    print("========== GRAPH RESULT ==========")
    print(result)
    print("==================================")


    snapshot = compiled_graph.get_state(config)

    print("========== SNAPSHOT ==========")
    print(snapshot.values)
    print("==============================")

    print("========== STATE HISTORY ==========")

    for state in compiled_graph.get_state_history(config):
      print("-----")
      print("NEXT:", state.next)
      print("VALUES:", state.values)

    print("===================================")
 
    final = result.get("final_analysis")
    is_finished = bool(final) and not result.get("current_question")

    return {
        "interview_id": request.interview_id,
        "question": result.get("current_question"),
        "message": "Thanks, that wraps up your interview." if is_finished else result.get("transition_message"),
        "candidate_answer": request.answer,
        "score": result.get("score"),
        "feedback": result.get("feedback"),
        "difficulty": result.get("difficulty"),
        "final_analysis": final,
        "finished": is_finished,
    }