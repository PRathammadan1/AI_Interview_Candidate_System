import re

from langchain_text_splitters import RecursiveCharacterTextSplitter

# Resume ke section ke naam -> ek standard naam
SECTION_WORDS = {
    "SUMMARY": ["summary", "objective", "profile", "about me", "career objective"],
    "EDUCATION": ["education", "academic", "qualification"],
    "SKILLS": ["skills", "technical skills", "technologies", "tech stack", "tools", "core competencies"],
    "PROJECTS": ["projects", "project", "academic projects", "personal projects", "key projects"],
    "EXPERIENCE": ["experience", "work experience", "internship", "internships", "training",
                   "professional experience", "employment", "work history"],
    "OTHER": ["certifications", "certification", "achievements", "awards", "courses",
              "extracurricular", "activities", "hobbies", "interests", "languages", "references"],
}
HEADING_MAP = {w: name for name, words in SECTION_WORDS.items() for w in words}


def _heading_of(line):
    """Line agar section ka heading hai to uska standard naam lautao, warna None."""
    s = re.sub(r"[^A-Za-z ]", " ", line).strip().lower()
    s = re.sub(r"\s+", " ", s)
    if not s or len(line.strip()) > 45:
        return None
    return HEADING_MAP.get(s)


def _inner_split(text, size=600, overlap=0):
    splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap)
    return splitter.split_text(text)


def split_text(text):
    sections = []                      # [(naam, [lines])]
    current, buf = "HEADER", []
    for ln in text.splitlines():
        name = _heading_of(ln)
        if name:
            if "".join(buf).strip():
                sections.append((current, buf))
            current, buf = name, []
        else:
            buf.append(ln)
    if "".join(buf).strip():
        sections.append((current, buf))

    # Koi heading nahi mila: purana tareeka
    if len(sections) <= 1 and sections and sections[0][0] == "HEADER":
        return _inner_split(text, 500, 50)

    chunks = []
    for name, body in sections:
        body_text = "\n".join(body).strip()
        if not body_text:
            continue
        # Har chunk apne section ke andar hi rahega, aur label ke saath
        for part in _inner_split(body_text):
            part = part.strip()
            if part:
                chunks.append(f"[{name}] {part}")
    return chunks or _inner_split(text, 500, 50)