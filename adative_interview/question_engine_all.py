import json
import random
import re

from backend.retrivel import retrieve
from langchain_ollama import ChatOllama

# # question_bank.py ho to bank ke sawal use honge, nahi ho to model ke
# try:
#     from adative_interview.question_bank import bank_question
# except ImportError:
    # bank_question = None

# Sawal ke shabdon mein variety ke liye thoda temperature
llm = ChatOllama(model="gemma3:4b", temperature=0.4, think=False)
# Core concepts nikalne ke liye stable output
json_llm = ChatOllama(model="gemma3:4b", temperature=0, format="json", think=False)

BAD_WORDS = [
    "great", "thorough", "excellent", "interesting", "impressive",
    "amazing", "fantastic", "wonderful", "perfect", "awesome", "nice",
    "i understand", "you're exploring", "you are exploring", "delve", "dive in",
    "good", "solid", "strong", "better", "correct",
    "clear", "clearly", "nicely", "helpful",
]
JUDGE_PHRASES = ["that's a", "that is a", "common approach", "good approach"]

FALLBACK_ACKS = [
    "Okay, got it. Let's move on.",
    "Alright, thanks for explaining. Next question.",
    "Thanks, noted. Let's continue.",
    "Okay, makes sense. Moving on.",
    "Alright, understood. Let's go to the next one.",
    "Okay, thanks for that. Here's the next question.",
    "Got it. Let's keep going.",
]
INTRO_ACKS = [
    "Thanks for the introduction. Let's move on to the next question.",
    "Okay, thanks for introducing yourself. Let's get started.",
]

KIND_STYLES = {
    "project": ("Ask about {topic}: what problem it solves, and which part was technically the "
                "hardest or which technical choice the candidate made, and why. "
                "Use only details that appear in the resume text. "
                "Do not assume any database, framework or tool that the resume does not mention. "
                "Do not mention any internship or company."),
    "keyword": ("Ask a TECHNICAL question that names {topic} explicitly and tests one core concept "
                "of it: how it works internally. Do not ask about benefits, advantages or speed."),
    "open": ("Ask ONE TECHNICAL question that names {topic} explicitly. It may be a short realistic "
             "scenario (an error, slow behaviour or a wrong result) with a question on how to find "
             "and fix it, or a question on how a feature works internally. "
             "Do not ask about benefits, advantages or speed."),
    "internship": ("Ask about {topic}: what the candidate's role was, the most useful thing they "
                   "learned, and one challenge they faced. Be warm and open so they can explain at length."),
}

DIFFICULTY_GUIDE = {
    "easy": "Keep the depth basic: a core idea a beginner could explain.",
    "normal": "Ask how it works and when to use it, with one concrete example.",
    "hard": "Ask about internals, trade-offs, edge cases or performance.",
}

# Koi example nahi: examples ka topic model utha leta tha
DEPTH_NOTE = ("The question must test real understanding: ask WHY or HOW something works, "
              "or how to find and fix one specific problem. Do not ask for a plain definition.")

SKILL_SUBTOPICS = {
    "java": [
        "the four OOP pillars (encapsulation, inheritance, polymorphism, abstraction)",
        "multithreading and thread safety (synchronized, race conditions)",
        "collections, especially how HashMap works internally",
        "exception handling (checked vs unchecked)",
        "JVM memory and garbage collection",
    ],
    "python": [
        "the GIL and threading vs multiprocessing",
        "decorators and generators",
        "lists, tuples, sets and dictionaries and their time complexity",
        "exception handling and context managers",
        "how memory management and mutable default arguments work",
    ],
    "angular": [
        "components and data binding",
        "the component lifecycle hooks",
        "services and dependency injection",
        "RxJS observables vs promises",
        "change detection",
    ],
    "react": [
        "state vs props and re-rendering",
        "useEffect and its dependency array",
        "the virtual DOM and keys in lists",
    ],
    "spring boot": [
        "auto-configuration and how beans are created",
        "dependency injection and bean scopes",
        "REST controllers and exception handling",
        "JPA/Hibernate and the N+1 query problem",
    ],
    "sql": [
        "joins and when each type is used",
        "indexes and how they affect reads and writes",
        "normalization",
        "ACID properties and transactions",
    ],
    "mysql": [
        "indexes and how they affect query speed",
        "transactions and isolation levels",
        "joins and query optimization",
    ],
    "javascript": [
        "closures and scope",
        "promises, async/await and the event loop",
        "var, let and const, and hoisting",
    ],
    "node": [
        "the event loop and non-blocking I/O",
        "middleware in Express",
        "handling errors in async code",
    ],
    "docker": [
        "images vs containers and layers",
        "volumes and networking",
    ],
    "aws": [
        "EC2 vs Lambda and when to use each",
        "S3 storage classes and access control",
        "IAM roles and least privilege",
        "VPC, subnets and security groups",
    ],
    "html": ["semantic HTML and accessibility", "the box model and layout basics"],
    "css": ["the box model", "flexbox vs grid", "specificity and the cascade"],
    "rest": [
        "HTTP methods and idempotency",
        "status codes and error handling",
        "statelessness and versioning",
    ],
    "jdbc": [
        "PreparedStatement vs Statement and SQL injection",
        "connection pooling",
        "transactions with commit and rollback",
    ],
    "hibernate": [
        "lazy vs eager loading",
        "the N+1 query problem",
        "entity states and the session cache",
    ],
    "mongodb": ["documents vs relational tables", "indexes and aggregation"],
    "git": ["branching and merging", "rebase vs merge", "resolving conflicts"],
    "linux": ["file permissions", "processes and signals"],
    "flask": ["routing and request context", "blueprints and app structure"],
    "django": ["the ORM and migrations", "the MVT pattern and middleware"],
    "fastapi": ["dependency injection and Pydantic validation", "async endpoints"],
}
LANGUAGES = {"java", "python", "javascript", "c++", "c#", "go", "kotlin", "typescript"}
VAGUE_WORDS = ("the framework", "the tool", "the technology", "the library", "the language")

_SUBTOPIC_CACHE = {}


def _matches(skill, key):
    return re.search(rf"(?<![a-z]){re.escape(key)}(?![a-z])", skill.lower()) is not None


def skill_rank(skill):
    if any(_matches(skill, k) for k in LANGUAGES):
        return 0          # language sabse pehle
    if any(_matches(skill, k) for k in SKILL_SUBTOPICS):
        return 1          # list wali skill
    return 2              # baaki


def ordered_skills(skills):
    # sorted stable hai: shuffle ka order har rank ke andar bana rehta hai
    return sorted(skills, key=skill_rank)


def make_plan(topics, total):
    skills = ordered_skills(topics.get("skills", []))
    plan = {}
    if not skills:
        return plan

    n = len(skills)
    keyword_qs = [3, 5, 7] if total >= 10 else [3]
    open_qs = [4, 6, 8, 9] if total >= 10 else [4]

    for i, q in enumerate(keyword_qs):
        # skills kam hon to skill dobara aayegi, par subtopic alag hoga
        plan[str(q)] = {"skill": skills[i % n], "sub": i // n}

    start = len(keyword_qs)
    for j, q in enumerate(open_qs):
        plan[str(q)] = {"skill": skills[(start + j) % n], "sub": None}
    return plan


def generate_subtopics(skill):
    """List mein na hone wali skill ke core concepts model se nikalo (ek baar, cache ke saath)."""
    key = skill.lower().strip()
    if key in _SUBTOPIC_CACHE:
        return _SUBTOPIC_CACHE[key]

    prompt = f"""List 4 core concepts of "{skill}" that an interviewer would ask a fresher about.

Rules:
- Only include concepts you are sure about.
- If you do not know this technology well, return an empty list.
- Each concept must be a short phrase.

Return ONLY JSON: {{"concepts": ["concept 1", "concept 2", "concept 3", "concept 4"]}}"""

    concepts = []
    try:
        content = json_llm.invoke(prompt).content.strip()
        data = json.loads(content[content.find("{"): content.rfind("}") + 1])
        concepts = [str(c).strip() for c in data.get("concepts", []) if str(c).strip()][:4]
    except Exception as e:
        print("Subtopic generation failed:", e)

    _SUBTOPIC_CACHE[key] = concepts
    return concepts


def pick_subtopic(skill, idx):
    for key in sorted(SKILL_SUBTOPICS, key=len, reverse=True):
        if _matches(skill, key):
            lst = SKILL_SUBTOPICS[key]
            return lst[idx % len(lst)]

    generated = generate_subtopics(skill)
    if generated:
        print("GENERATED SUBTOPICS for", skill, ":", generated)
        return generated[idx % len(generated)]

    print("NO SUBTOPIC FOR:", skill)
    return None


def question_kind(n, total):
    if n == 2:
        return "project"
    if n == total:
        return "internship"
    if total >= 10:
        return "keyword" if n in (3, 5, 7) else "open"
    return "keyword" if n == 3 else "open"        # 5 sawal wala mode


def pick_topic(state, n, total, plan):
    topics = state.get("topics") or {}
    projects = topics.get("projects", [])
    internships = topics.get("internships", [])
    kind = question_kind(n, total)

    if kind == "project" and projects:
        return f"the project '{projects[0]}'"
    if kind == "internship":
        if internships:
            return f"the internship '{internships[0]}'"
        return "the candidate's experience while learning and building projects"

    entry = plan.get(str(n))
    if entry:
        return entry["skill"]
    return "a technology mentioned in the resume"


def clean_acknowledgement(ack):
    print("RAW ACK:", ack)
    ack = (ack or "").strip()
    low = ack.lower()
    if (
        not ack
        or low.startswith("that's")
        or any(p in low for p in JUDGE_PHRASES)
        or any(w in low for w in BAD_WORDS)
    ):
        return random.choice(FALLBACK_ACKS)
    return ack


def clean_question(q, topic, technical):
    q = (q or "").strip()
    q = q.strip('"\'“”‘’').strip()
    q = re.sub(r"^you (mentioned|said|noted|listed)[^.,]*[.,]\s*", "", q, flags=re.I)
    if technical:
        for vague in VAGUE_WORDS:
            q = q.replace(vague, topic).replace(vague.capitalize(), topic)
    q = q[:1].upper() + q[1:]
    if q and not q.endswith("?"):
        q += "?"
    return q


def question_ok(q, skill, technical):
    """Halke ya galat format ke sawal pakadta hai."""
    words = len(q.split())
    if words < 8 or words > 45:
        return False
    if not technical:
        return True
    low = q.lower()
    if low.startswith(("how did you", "you mentioned")):
        return False
    if any(w in low for w in ("benefit", "advantage")):
        return False
    parts = [w for w in re.findall(r"[a-z0-9+#.]+", skill.lower()) if len(w) >= 2]
    if parts and not any(w in low for w in parts):      # technology ka naam sawal mein ho
        return False
    return True


def parse_json(content):
    content = content.replace("```json", "").replace("```", "").strip()
    start, end = content.find("{"), content.rfind("}") + 1
    try:
        return json.loads(content[start:end])
    except Exception as e:
        print("JSON FAILED:", e)
        return {}


def build_question(state, difficulty):
    previous_question = state["current_question"]
    candidate_answer = state["candidate_answer"]
    question_number = state["question_count"] + 1
    total = state.get("total_questions", 5)

    plan = state.get("plan") or make_plan(state.get("topics") or {}, total)
    entry = plan.get(str(question_number), {})

    kind = question_kind(question_number, total)
    topic = pick_topic(state, question_number, total, plan)
    style = KIND_STYLES[kind].format(topic=topic)
    technical = kind in ("keyword", "open")

    if kind == "keyword":
        sub = pick_subtopic(topic, entry.get("sub", 0))
        if sub:
            style += f" Focus on this core concept: {sub}."
            print("SUBTOPIC:", sub)
        else:
            style += (f" Base the question on what the resume says about {topic}. "
                      f"Ask about one specific technical detail from it, not a general definition.")

    if kind == "project":
        wording = "You may mention the project name."
        guard, depth_line = "", DIFFICULTY_GUIDE[difficulty]
    elif kind == "internship":
        wording = "Be conversational. You may mention the internship."
        guard, depth_line = "", "Keep it open and conversational, not a quiz."
    else:
        wording = (
            "Do not assume what the candidate built or did. "
            "Always write the exact name of the technology in the question. "
            "Never say 'the framework', 'the tool' or 'the technology'. "
            "Do not ask about benefits, advantages or development speed. "
            "Start with 'What', 'Why', 'How does', 'How would you' or a short problem. "
            "Never start with 'How did you'. "
            "Never start with 'You mentioned', 'You said' or 'You listed'."
        )
        guard = " Do not mention any project name."
        depth_line = DIFFICULTY_GUIDE[difficulty] + " " + DEPTH_NOTE

    question_instruction = (
        f"{style} Ask ONE question about {topic} only. "
        f"Do not mention any other technology.{guard}"
    )
    print("QUESTION NUMBER:", question_number, "of", total, "| KIND:", kind, "| TOPIC:", topic)

    resume_context = retrieve(f"{topic} experience and usage")

    asked = []
    for h in state.get("interview_history", []):
        q = h.get("question") if isinstance(h, dict) else str(h)
        if q:
            asked.append(q)
    asked.append(previous_question)
    asked_text = "\n".join(f"- {q}" for q in asked)

    prompt = f"""You are a friendly technical interviewer.

Previous question you asked:
"{previous_question}"

Candidate's answer:
"{candidate_answer}"

Resume:
{resume_context}

Questions already asked (do NOT repeat these):
{asked_text}

Do these two things:

1. acknowledgement: Say ONE short, casual sentence (max 12 words) the way a real
   interviewer would after hearing an answer.
   - Keep it neutral. Do not praise or judge the answer.
   - Never use words like "great", "thorough", "excellent", "interesting", "impressive", "nice", "good", "clear".
   - Start with a natural reaction like: "Got it", "Okay", "Alright", "Makes sense", "Thanks".
   - Never start with "I understand" or "That's".
   - Do not ask a question. Do not give a score.

2. next_question: {question_instruction}
   - {wording}
   - Use only technologies present in the resume.
   - The question must focus on ONE single topic only.
   - Keep the question under 40 words.
   - Do not wrap the question in quotation marks.
   - Difficulty level: {difficulty.upper()}.
   - {depth_line}
   - Write exactly ONE question.

Return ONLY a JSON object with the keys "acknowledgement" and "next_question".
Do not copy any wording from the instructions above.
"""

    # Sawal banao; halka ya galat laga to ek baar aur try karo
    result, question = {}, ""
    for attempt in range(2):
        response = llm.invoke(prompt)
        content = response.content.strip()
        print(f"\n===== {difficulty.upper()} QUESTION RAW RESPONSE (try {attempt + 1}) =====")
        print(content)
        print("=======================================================")
        result = parse_json(content)
        question = clean_question(result.get("next_question"), topic, technical)
        if question and question_ok(question, topic, technical):
            break
        print("QUESTION REJECTED, retrying:", question)

    # Bank ka sawal (agar bank file hai): depth ki guarantee
    # if bank_question and technical:
    #     idx = entry.get("sub")
    #     if idx is None:
    #         idx = random.randint(0, 9)
    #     bq = bank_question(topic, idx, difficulty, asked)
    #     if bq:
    #         question = bq
    #         print("BANK QUESTION USED:", topic, idx, difficulty)

    # if not question:
    #     question = f"What is {topic} and how does it work?"

    if state["question_count"] == 1:
        ack = random.choice(INTRO_ACKS)
    else:
        ack = clean_acknowledgement(result.get("acknowledgement"))

    return {
        "current_question": question,
        "transition_message": ack,
        "plan": plan,
        "difficulty": difficulty,
    }