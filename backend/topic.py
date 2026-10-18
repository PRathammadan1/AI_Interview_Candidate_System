import json
import random

from langchain_ollama import ChatOllama
from backend.retrivel import retrieve

extract_llm = ChatOllama(model="gemma3:4b", temperature=0, format="json", think=False)

LOW_PRIORITY = {"pandas", "numpy", "matplotlib", "seaborn", "python", "sql", "git", "github"}
GENERIC = {
    "networking", "cloud computing", "cloud", "programming", "coding",
    "web development", "database", "databases", "software development",
    "problem solving", "communication", "teamwork", "internship",
}


def _clean(items, limit):
    seen, out = set(), []
    for x in items or []:
        s = str(x).strip()
        if s and s.lower() not in seen:
            seen.add(s.lower())
            out.append(s)
    return out[:limit]


def extract_topics():
    projects_ctx = retrieve("projects built by the candidate")
    skills_ctx = retrieve("technical skills, programming languages, frameworks, tools")
    intern_ctx = retrieve("internship, work experience, training, company")

    prompt = f"""Read this resume text and extract information.

Projects section:
{projects_ctx}

Skills section:
{skills_ctx}

Experience section:
{intern_ctx}

Return ONLY JSON in this format:
{{"projects": ["project name 1", "project name 2"],
  "skills": ["skill 1", "skill 2", "skill 3", "skill 4"],
  "internships": ["role and company or program name"]}}

Rules:
- Use only things written in the text above.
- Maximum 3 projects, 8 skills and 2 internships.
- Skills must be specific technologies (like FastAPI, FAISS), not generic words.
- If there is no internship or work experience, return an empty list for internships.
"""
    try:
        content = extract_llm.invoke(prompt).content.strip()
        content = content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content[content.find("{"): content.rfind("}") + 1])
        topics = {
            "projects": _clean(data.get("projects"), 3),
            "skills": _clean(data.get("skills"), 8),
            "internships": _clean(data.get("internships"), 2),
        }
    except Exception as e:
        print("Topic extraction failed:", e)
        topics = {"projects": [], "skills": [], "internships": []}

    topics["skills"] = [s for s in topics["skills"] if s.lower() not in GENERIC]

    random.shuffle(topics["projects"])
    random.shuffle(topics["skills"])
    topics["skills"].sort(key=lambda s: s.lower() in LOW_PRIORITY)

    print("TOPICS:", topics)
    return topics
