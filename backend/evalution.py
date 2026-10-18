from langchain_ollama import ChatOllama
import json
import os
# from dotenv import load_dotenv
# from google import genai

# load_dotenv()

# client = genai.Client()


llm = ChatOllama(
    model="gemma3:1b",
    temperature=0
)


def evaluate_answer(question, answer, context):

    prompt = f"""
You are a strict technical interview evaluator.

Your task is to evaluate the candidate's answer ONLY against
the Interview Question.

========================
MOST IMPORTANT RULE
========================

The Interview Question defines EXACTLY what the candidate
is expected to answer.

Do NOT evaluate the candidate against the resume.

Do NOT evaluate the candidate against information that is
not explicitly required by the Interview Question.

Do NOT create additional requirements.

========================
INTERVIEW QUESTION
========================

{question}

========================
CANDIDATE ANSWER
========================

{answer}

========================
EVALUATION METHOD
========================

Step 1:
Identify the main things explicitly requested by the Interview Question.

Step 2:
Check which of those things the Candidate Answer actually provides.

Step 3:
Give credit ONLY for information explicitly stated in the
Candidate Answer.

Step 4:
Identify Missing Points ONLY from the requirements of the
Interview Question.

Do NOT use your general knowledge to create additional
requirements.

========================
STRENGTH RULE
========================

A strength must be directly supported by the Candidate Answer.

Never invent a strength.

Never infer information that the candidate did not say.

========================
MISSING POINT RULE
========================

A missing point is valid ONLY if the Interview Question
explicitly requires that information and the Candidate Answer
does not provide it.

For example, if the question asks:

"Explain what problem your project was designed to solve."

Then valid missing points include:

- The specific problem was not clearly identified.
- The target problem was described too generally.

Invalid missing points include:

- LLM model
- RAG
- LangChain
- Python
- SQL
- architecture
- implementation
- prompting
- workflow
- task management
- journaling

unless the Interview Question explicitly asks about them.

Incorrect evaluation:

- Missing LLM details.
- Missing architecture.
- Missing implementation.
- Missing technologies.
- Missing RAG.
- Missing task management.

These are NOT required by the question.

========================
SCORE
========================

Score the answer from 0 to 10.

Base the score ONLY on:

- Relevance to the question
- Clarity
- Completeness of the requested information
- Technical correctness of claims actually made

Do not reduce the score because the candidate omitted
information that the question did not ask for.

========================
FINAL SELF-CHECK
========================

Before returning the evaluation:

For EVERY strength ask:

"Did the candidate actually say this?"

For EVERY missing point ask:

"Does the question actually require this?"

For EVERY feedback statement ask:

"Is this based only on the question and candidate answer?"

If the answer is NO, remove the statement.

========================
OUTPUT
========================

Return ONLY valid JSON.

{{
  "score": 0,
  "strengths": [],
  "missing_points": [],
  "feedback": ""
}}

Rules:

- score must be an integer from 0 to 10.
- strengths must be a JSON array of strings.
- missing_points must be a JSON array of strings.
- feedback must be a single string.
- No Markdown.
- No explanation outside JSON.
""" 


    raw_response = llm.invoke(prompt)

    if raw_response.startswith("```json"):
      raw_response = raw_response[7:]

    if raw_response.endswith("```"):
       raw_response = raw_response[:-3]

    raw_response = raw_response.strip()

    evaluation = json.loads(raw_response)

    return evaluation