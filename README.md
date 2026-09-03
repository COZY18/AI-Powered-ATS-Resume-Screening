[README.md](https://github.com/user-attachments/files/31808812/README.md)
# 🎯 Resume-to-Job Matcher AI

> **An intelligent NLP tool that scores your resume against a job description and tells you *exactly* why — missing skills, keyword gaps, semantic similarity, and actionable recommendations.**

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40-red)
![spaCy](https://img.shields.io/badge/spaCy-3.7-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ What Makes This Different?

Most resume scanners give you a vague "match percentage." This tool goes deeper:

| Feature | What It Does |
|---------|-------------|
| 🔍 **Semantic Similarity** | Understands *meaning*, not just keywords. "Backend developer" ≈ "Server-side engineer" |
| 🧠 **Named Entity Recognition** | Auto-extracts names, companies, locations, dates using spaCy |
| 📊 **Skill Gap Analysis** | Shows exactly which skills you're missing vs. what the job wants |
| 🎁 **Bonus Skills Detection** | Highlights skills you have that the job didn't ask for (negotiation leverage!) |
| 👔 **Experience Level Match** | Detects junior/senior/manager level alignment |
| 💡 **Explainable AI** | Human-readable explanations + actionable recommendations |

---

## 🚀 Live Demo

🌐 **[Try it live on Streamlit Cloud](YOUR_DEPLOYED_URL_HERE)**

Or run it locally in 30 seconds:

```bash
git clone https://github.com/YOUR_USERNAME/resume-matcher-ai.git
cd resume-matcher-ai
pip install -r requirements.txt
python -m spacy download en_core_web_lg
streamlit run app.py
```

---

## 📸 Screenshots

### Dashboard View
```
┌─────────────────────────────────────────────────────────────┐
│  📄 Resume-to-Job Matcher AI                                │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Overall  │  │ Semantic │  │ Keyword  │  │ Skills   │  │
│  │   72%    │  │   78%    │  │   45%    │  │  8/12    │  │
│  │   🎉     │  │          │  │          │  │          │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                             │
│  🧠 AI Explanation                                          │
│  → Strong Semantic Match: Your resume and job description   │
│    are highly aligned in meaning...                         │
│                                                             │
│  🔴 Missing Skills (4): kubernetes, terraform, gcp, kafka   │
│  ✅ Matching Skills (8): python, django, docker, aws...      │
│  🟢 Bonus Skills (2): photoshop, illustrator                │
│                                                             │
│  💡 Recommendations                                         │
│  1. Add Missing Skills: Consider adding kubernetes...        │
│  2. Increase Keyword Density: Use more exact phrases...      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RESUME MATCHER AI                         │
├─────────────────────────────────────────────────────────────┤
│  INPUT LAYER                                                │
│  ├── PDF/DOCX/TXT Resume  →  PyPDF2 / python-docx          │
│  └── Job Description      →  Direct text input              │
├─────────────────────────────────────────────────────────────┤
│  ANALYSIS LAYER (matcher.py - The Brain)                    │
│  ├── Text Cleaning        →  regex, lowercase, normalize    │
│  ├── NER Extraction       →  spaCy (names, orgs, dates)    │
│  ├── Skill Matching       →  Dictionary lookup + regex      │
│  ├── Semantic Similarity  →  Sentence-Transformer + Cosine  │
│  ├── Keyword Overlap      →  Jaccard Similarity             │
│  ├── Experience Detection →  Keyword pattern matching       │
│  └── Explanation Gen      →  Conditional logic + templates  │
├─────────────────────────────────────────────────────────────┤
│  OUTPUT LAYER (app.py - The Face)                           │
│  ├── Overall Score (70% semantic + 30% keyword)            │
│  ├── Semantic Score (meaning-based match)                   │
│  ├── Keyword Score (exact word overlap)                     │
│  ├── Skills Breakdown (match/missing/extra)                │
│  ├── Experience Level Analysis                              │
│  ├── AI Explanation (human-readable why)                    │
│  └── Actionable Recommendations                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 The Science Behind It

### 1. Named Entity Recognition (NER)
Using **spaCy**'s `en_core_web_lg` model, the tool automatically identifies:
- **PERSON** → Candidate names
- **ORG** → Companies worked at
- **GPE** → Locations (cities, countries)
- **DATE** → Time periods

### 2. Semantic Similarity (The Magic)
**Sentence-Transformers** (`all-MiniLM-L6-v2`) converts text into 384-dimensional vectors. Two sentences with similar meaning produce similar vectors, even if they use completely different words.

**Example:**
- Resume: *"I build web applications using Python frameworks"*
- Job: *"Looking for someone who develops backend systems with Python"*
- **Keyword match:** LOW (different words)
- **Semantic match:** HIGH (same meaning!)

### 3. Cosine Similarity
Measures the angle between two vectors:
- `1.0` = identical meaning
- `0.7+` = very similar
- `0.4-0.7` = somewhat similar
- `< 0.4` = different meanings

### 4. Scoring Algorithm
```
Overall Score = (Semantic × 0.7) + (Keyword × 0.3) - Skill Penalty

Where:
- Semantic = 70% weight (meaning matters more than exact words)
- Keyword = 30% weight (exact matches still count)
- Skill Penalty = min(missing_skills × 2, 20) points max
```

---

## 📁 Project Structure

```
resume-matcher-ai/
│
├── 📄 requirements.txt          # Python dependencies
├── 🧠 matcher.py               # Core NLP logic & analysis engine
├── 🎨 app.py                   # Streamlit web interface
├── 📖 README.md                # This file
│
└── .gitignore                  # Ignore __pycache__, .env, etc.
```

| File | Purpose | Lines |
|------|---------|-------|
| `requirements.txt` | Lists all Python libraries needed | ~10 |
| `matcher.py` | The brain: NER, embeddings, scoring, explanations | ~250 |
| `app.py` | The face: UI, file upload, results dashboard | ~200 |

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **UI Framework** | Streamlit | Pure Python, no HTML/CSS/JS needed |
| **NER** | spaCy (`en_core_web_lg`) | Production-grade entity extraction |
| **Embeddings** | Sentence-Transformers | State-of-the-art semantic understanding |
| **Similarity** | scikit-learn (cosine) | Fast, reliable vector math |
| **File Parsing** | PyPDF2, python-docx | Reads PDF & Word resumes |
| **Language** | Python 3.10+ | Clean, readable, beginner-friendly |

---

## 🚦 Getting Started

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- ~2GB free space (for spaCy large model)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/resume-matcher-ai.git
cd resume-matcher-ai

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download spaCy language model (~500MB)
python -m spacy download en_core_web_lg

# 5. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📝 Usage

1. **Upload or paste your resume** (supports PDF, DOCX, TXT)
2. **Paste the job description** you're applying for
3. **Click "Analyze Match"**
4. **Review the dashboard:**
   - Overall match score
   - Semantic similarity (meaning-based)
   - Keyword overlap (exact words)
   - Skills breakdown (match / missing / bonus)
   - Experience level alignment
   - AI-generated explanation
   - Actionable recommendations

---

## 🧪 Example Test Case

### Sample Resume
```
John Doe
Software Engineer with 5 years of experience

Skills: Python, Django, React, SQL, Docker, AWS
Worked at TechCorp as Senior Developer
Led a team of 3 engineers
Built REST APIs and microservices
Experience with CI/CD pipelines and Git
```

### Sample Job Description
```
Senior Python Developer
We are looking for a senior developer with 5+ years of experience

Required skills: Python, Django, REST API, Docker, Kubernetes
Experience with AWS and microservices architecture
Leadership skills and team management required
Knowledge of CI/CD and Git workflows
```

### Expected Results
| Metric | Value |
|--------|-------|
| Overall Score | ~70% |
| Semantic Score | ~78% |
| Keyword Score | ~45% |
| Matching Skills | python, django, docker, rest api, aws, ci/cd, git |
| Missing Skills | kubernetes |
| Bonus Skills | react, sql |
| Experience Level | ✅ Senior (matches!) |

---

## 🎓 What I Learned Building This

This project taught me:

- **NLP Pipeline Design** → How to chain preprocessing → NER → embedding → scoring
- **Semantic vs. Syntactic Matching** → Why meaning > keywords
- **Explainable AI** → Users need reasons, not just scores
- **File Format Handling** → Parsing PDFs and Word docs reliably
- **Weighted Scoring** → Combining multiple signals intelligently
- **Streamlit for Rapid Prototyping** → From idea to live app in hours

---

## 🚀 Future Improvements

- [ ] **ATS Parser** → Handle complex resume layouts (columns, tables)
- [ ] **Skill Database** → Connect to LinkedIn/Indeed APIs for trending skills
- [ ] **Resume Optimizer** → Auto-suggest rewrites for missing keywords
- [ ] **Batch Processing** → Compare one resume against 100 jobs at once
- [ ] **Cover Letter Generator** → AI-generated cover letter based on gaps
- [ ] **History & Tracking** → Save analyses over time to see improvement
- [ ] **Dark Mode** → Because developers love dark mode

---

## 🤝 Why I Built This

> I was applying to jobs and sending the same resume everywhere with zero feedback. I had no idea if I was even close to what companies wanted. So I built this tool to get *actionable* insights — not just a number, but a clear breakdown of what's missing and how to fix it. I literally use it for every job application now.

---

## 📄 License

MIT License — feel free to use, modify, and share!

---

## 🙏 Acknowledgments

- [spaCy](https://spacy.io/) for industrial-strength NLP
- [Sentence-Transformers](https://www.sbert.net/) for semantic embeddings
- [Streamlit](https://streamlit.io/) for making web apps effortless

---

<p align="center">
  <b>⭐ Star this repo if it helped you land an interview!</b>
</p>
