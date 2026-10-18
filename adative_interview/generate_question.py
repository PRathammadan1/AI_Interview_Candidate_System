from adative_interview.state import InterviewState
from backend.retrivel import retrieve
# from langchain_google_genai import ChatGoogleGenerativeAI
# from dotenv import load_dotenv
# from google import genai
from langchain_ollama import ChatOllama

llm = ChatOllama(
     model="gemma3:4b",
     temperature=0,
 )


# load_dotenv()

# client = genai.Client()



# llm = ChatGoogleGenerativeAI(
#     model="gemini-3.6-flash",
# )


# def generate_question(state: InterviewState):

#     # Resume se relevant information retrieve karo
#     resume_context = retrieve(
#         "candidate skills, projects, experience and technical background"
#     )

#     # Gemini ke liye prompt
#     prompt = f"""
# You are an AI technical interviewer.

# Generate ONE interview question based ONLY on the candidate's resume.

# Candidate resume information:
# {resume_context}

# Rules:
# 1. Ask exactly ONE question.
# 2. The question must be directly related to something explicitly
#    mentioned in the resume.
# 3. Focus on ONE project, skill, technology, experience, or achievement
#    at a time.
# 4. Do not combine multiple topics in one question.
# 5. Do not assume or invent any information that is not present in the resume.
# 6. Do not ask about technologies or concepts that are not mentioned
#    in the resume.
# 7. Prefer questions that ask the candidate to explain their own work
#    or experience.
# 8. Keep the question clear, natural, and suitable for a technical interview.
# 9. Return ONLY the question. Do not provide an answer or explanation.

# Generate the interview question now.
# """

#     # Gemini ko LangChain ke through call karo
#     response = llm.invoke(prompt)
#     # question= response.content[0]["text"]
#     question = response.content
#     # State update karo
#     return {
#          "current_question": question
#     }

# if __name__ == "__main__":
#     state = {
#         "current_question": "",
#         "candidate_answer": "",
#         "score": 0,
#         "strengths": [],
#         "missing_points": [],
#         "feedback": "",
#         "difficulty": "normal",
#         "interview_history": []
#     }

#     result = generate_question(state)

#     print("Generated Question:")
#     print(result["current_question"])
def generate_question(state: InterviewState):
    
    prompt =    f"""
You are a professional AI technical interviewer conducting a natural,
candidate-friendly interview.

Candidate Name:
{state["name"]}

Generate exactly ONE opening interview question for this candidate.

IMPORTANT:
- Use the candidate name provided above.
- The candidate name is "{state["name"]}".
- NEVER use any other name.
- Do not copy a name from an example.
- Do not invent or assume a different candidate name.

The question MUST:
- Start with a warm but professional welcome using the candidate's exact name.
- Thank the candidate for joining the interview.
- Naturally transition into the introduction.
- Ask the candidate to briefly introduce themselves and share a little
  about their background.
- Sound like a real human interviewer.
- Be concise and conversational.
- Do not ask about projects, technologies, skills, strengths,
  weaknesses, or job motivation yet.
- Do not mention the resume yet.
- Ask only ONE question.
- Return ONLY the interview question.
- Do not use quotation marks.
- Do not use markdown.

Generate the opening question now.

"""

    response = llm.invoke(prompt)



    question = response.content

    return {
        "current_question": question
    }