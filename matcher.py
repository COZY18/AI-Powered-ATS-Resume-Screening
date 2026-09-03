"""
matcher.py — Core NLP engine for Resume-to-Job Matcher AI

Responsibilities:
  1. Extract skills from raw text using a curated skill taxonomy + spaCy phrase matching
  2. Compute semantic similarity between resume and job description (sentence embeddings)
  3. Compute keyword overlap (TF-IDF cosine)
  4. Detect experience level (entry / mid / senior) from text cues
  5. Combine everything into a single explainable result dict consumed by app.py
"""

import re
import spacy
from spacy.matcher import PhraseMatcher
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------------------------
# Lazy-loaded globals (loaded once per process, not per request)
# ---------------------------------------------------------------------------
_nlp = None
_embedder = None

def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_lg")
        except OSError:
            # fallback if the large model isn't downloaded
            _nlp = spacy.load("en_core_web_sm")
    return _nlp

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder

# ---------------------------------------------------------------------------
# Skill taxonomy — extend this freely, it's the heart of the matcher
# ---------------------------------------------------------------------------
SKILL_TAXONOMY = [
    # Languages
    "python", "java", "c++", "c", "javascript", "typescript", "go", "rust", "sql", "r",
    # Web / Backend
    "react", "node.js", "django", "flask", "fastapi", "express", "spring boot",
    "rest api", "graphql", "html", "css", "next.js",
    # Data / ML
    "machine learning", "deep learning", "nlp", "computer vision", "pytorch",
    "tensorflow", "scikit-learn", "keras", "opencv", "yolo", "pandas", "numpy",
    "data analysis", "data visualization", "llm", "transformers",
    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "jenkins", "terraform",
    "cloud computing", "linux", "git", "github actions",
    # Databases
    "mysql", "postgresql", "mongodb", "redis", "database design", "nosql",
    # Fundamentals
    "data structures", "algorithms", "dsa", "system design", "oop",
    "object oriented programming", "agile", "scrum",
]

EXPERIENCE_CUES = {
    "entry": ["intern", "internship", "fresher", "entry level", "0-1 year", "recent graduate",
              "final year", "b.tech", "undergraduate"],
    "mid": ["2-4 years", "3+ years", "mid level", "associate", "2 years", "3 years", "4 years"],
    "senior": ["senior", "lead", "5+ years", "6+ years", "principal", "staff engineer",
               "architect", "manager", "10+ years", "head of"],
}


def _build_phrase_matcher(nlp):
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(skill) for skill in SKILL_TAXONOMY]
    matcher.add("SKILLS", patterns)
    return matcher


def extract_skills(text: str) -> set:
    """Extract known skills present in a block of text."""
    nlp = get_nlp()
    doc = nlp(text.lower())
    matcher = _build_phrase_matcher(nlp)
    matches = matcher(doc)
    found = set()
    for match_id, start, end in matches:
        found.add(doc[start:end].text.strip())
    return found


def extract_text_from_resume(text: str) -> str:
    """Light cleanup pass — normalises whitespace, strips control chars."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def detect_experience_level(text: str) -> str:
    text_lower = text.lower()
    scores = {level: 0 for level in EXPERIENCE_CUES}
    for level, cues in EXPERIENCE_CUES.items():
        for cue in cues:
            if cue in text_lower:
                scores[level] += 1
    if max(scores.values()) == 0:
        return "mid"  # neutral default when no strong signal
    return max(scores, key=scores.get)


def semantic_similarity(resume_text: str, job_text: str) -> float:
    model = get_embedder()
    emb1 = model.encode(resume_text, convert_to_tensor=True)
    emb2 = model.encode(job_text, convert_to_tensor=True)
    score = util.cos_sim(emb1, emb2).item()
    return round(max(0, min(100, score * 100)), 1)


def keyword_overlap_score(resume_text: str, job_text: str) -> float:
    try:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=500)
        tfidf = vectorizer.fit_transform([resume_text, job_text])
        sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return round(max(0, min(100, sim * 100)), 1)
    except ValueError:
        return 0.0


def generate_explanation(overall, semantic, keyword, matching, missing, exp_match) -> str:
    lines = []
    if overall >= 75:
        lines.append(f"**Strong match ({overall}%).** Your resume aligns well with this role both "
                      f"semantically and on keywords — you're a competitive candidate on paper.")
    elif overall >= 50:
        lines.append(f"**Moderate match ({overall}%).** You have a real foundation here, but there are "
                      f"clear gaps worth closing before applying.")
    else:
        lines.append(f"**Weak match ({overall}%).** This role may need a different skill emphasis, "
                      f"or your resume simply isn't using the job's language yet.")

    if semantic > keyword + 15:
        lines.append("Your resume reads *thematically* similar to the job, but doesn't share much "
                      "exact vocabulary — consider mirroring the job posting's specific terms.")
    elif keyword > semantic + 15:
        lines.append("You share a lot of exact keywords with the posting, but the overall narrative "
                      "may not emphasize the right themes — focus on framing your experience around "
                      "the job's core responsibilities.")

    if missing:
        top_missing = ", ".join(list(missing)[:5])
        lines.append(f"Skills mentioned in the job but not detected in your resume: **{top_missing}**.")

    if not exp_match:
        lines.append("There's a mismatch in seniority signals between your resume and the job listing.")

    return "\n\n".join(lines)


def match_resume_to_job(resume_text: str, job_text: str) -> dict:
    resume_text = extract_text_from_resume(resume_text)
    job_text = extract_text_from_resume(job_text)

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)

    matching_skills = resume_skills & job_skills
    missing_skills = job_skills - resume_skills
    extra_skills = resume_skills - job_skills

    semantic_score = semantic_similarity(resume_text, job_text)
    keyword_score = keyword_overlap_score(resume_text, job_text)

    resume_level = detect_experience_level(resume_text)
    job_level = detect_experience_level(job_text)
    exp_match = (resume_level == job_level)

    skill_ratio = (len(matching_skills) / len(job_skills) * 100) if job_skills else 100
    overall_score = round(0.4 * semantic_score + 0.3 * keyword_score + 0.3 * skill_ratio, 1)

    explanation = generate_explanation(
        overall_score, semantic_score, keyword_score,
        matching_skills, missing_skills, exp_match
    )

    return {
        "overall_score": overall_score,
        "semantic_score": semantic_score,
        "keyword_score": keyword_score,
        "matching_skills": sorted(matching_skills),
        "missing_skills": sorted(missing_skills),
        "extra_skills": sorted(extra_skills),
        "skill_match_count": len(matching_skills),
        "skill_gap_count": len(missing_skills),
        "explanation": explanation,
        "experience_analysis": {
            "resume_level": resume_level,
            "job_level": job_level,
            "match": exp_match,
        },
    }