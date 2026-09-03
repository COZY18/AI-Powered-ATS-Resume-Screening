import streamlit as st
import plotly.graph_objects as go
import PyPDF2
import docx
 
from matcher import match_resume_to_job
 
st.set_page_config(page_title="Resume Matcher AI", page_icon="🤖", layout="wide")
 
# ---------------------------------------------------------------------------
# THEME — glassmorphism, light, no dark mode. Strong overrides so Streamlit's
# dark-theme defaults on inputs/labels/buttons never leak through.
# ---------------------------------------------------------------------------
st.markdown("""
<style>
:root {
    --primary: #2563eb;
    --secondary: #4f46e5;
    --accent: #06b6d4;
    --bg: #f3f8ff;
    --card: #ffffff;
    --text: #1e293b;
    --muted: #64748b;
    --border: #d6e4ff;
    --success: #16a34a;
    --success-bg: #e9fbf0;
    --danger: #dc2626;
    --danger-bg: #fdecec;
}
 
.stApp {
    background: linear-gradient(135deg, #eef4ff, #f8fbff);
}
 
/* ---------- TEXT: force dark everywhere, kill Streamlit dark-theme leakage ---------- */
html, body, p, span, label, small, div, li,
h1, h2, h3, h4, h5, h6 {
    color: var(--text) !important;
}
.stMarkdown, .stCaption, [data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stCaptionContainer"],
[data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
    color: var(--text) !important;
}
 
/* ---------- INPUTS ---------- */
textarea, input {
    color: #111827 !important;
    background: #ffffff !important;
}
.stTextArea textarea {
    background: white !important;
    color: #111827 !important;
    border-radius: 14px;
    border: 2px solid var(--border);
}
.stTextArea textarea:focus {
    border: 2px solid var(--secondary) !important;
    outline: none;
    box-shadow: 0 0 15px rgba(79, 70, 229, 0.2);
}
textarea::placeholder, input::placeholder { color: #7c8799 !important; }
.stTextArea label, .stFileUploader label, [data-testid="stFileUploader"] label {
    color: var(--text) !important;
    font-weight: 600 !important;
}
 
/* ---------- FILE UPLOADER ---------- */
[data-testid="stFileUploaderDropzone"] {
    background: white;
    border: 2px dashed var(--secondary);
    border-radius: 16px;
    padding: 22px;
}
[data-testid="stFileUploaderDropzone"] * { color: var(--text) !important; }
 
/* ---------- BUTTON ---------- */
div.stButton > button {
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    color: white !important;
    border: none;
    font-weight: 700;
    padding: 14px;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(37, 99, 235, 0.25);
    transition: 0.3s;
    width: 100%;
}
div.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 18px 40px rgba(37, 99, 235, 0.4);
}
div.stButton > button p { color: white !important; }
 
/* ---------- HERO ---------- */
.hero {
    text-align: center;
    padding: 2.4rem 1rem 1.6rem 1rem;
    animation: fadeUp 0.6s ease;
}
.hero-badge {
    display: inline-block;
    background: rgba(37, 99, 235, 0.1);
    color: var(--primary) !important;
    font-weight: 700;
    font-size: 0.8rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 6px 16px;
    border-radius: 20px;
    margin-bottom: 1rem;
}
.hero-title {
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(90deg, #2563eb, #4f46e5, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}
.hero-sub {
    color: var(--muted) !important;
    font-size: 1.1rem;
    max-width: 640px;
    margin: 0 auto;
    line-height: 1.5;
}
.hero-divider {
    width: 90px;
    height: 4px;
    margin: 1.4rem auto 0 auto;
    border-radius: 4px;
    background: linear-gradient(90deg, #2563eb, #06b6d4);
}
 
/* ---------- GLASS CARDS ---------- */
.card {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 22px;
    padding: 1.7rem 1.8rem;
    box-shadow: 0 15px 45px rgba(0, 0, 0, 0.08);
    margin-bottom: 1.2rem;
    animation: fadeUp 0.5s ease;
}
.section-label {
    font-size: 0.82rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--primary) !important;
    margin-bottom: 0.6rem;
}
 
/* ---------- METRIC TILES ---------- */
.metric-tile {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 18px;
    border: 1px solid var(--border);
    padding: 1.3rem;
    text-align: center;
    box-shadow: 0 8px 22px rgba(37, 99, 235, 0.08);
}
.metric-tile .label {
    color: var(--muted) !important;
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.metric-tile .value {
    font-size: 2.3rem;
    font-weight: 900;
    margin-top: 0.2rem;
}
 
/* ---------- SKILL PILLS ---------- */
.pill {
    display: inline-block;
    padding: 7px 15px;
    margin: 4px 6px 4px 0;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 700;
}
.pill-match { background: var(--success-bg); color: #15803d !important; border: 1px solid #bbf0cf; }
.pill-missing { background: var(--danger-bg); color: #b91c1c !important; border: 1px solid #f7c9c9; }
.pill-extra { background: rgba(37, 99, 235, 0.08); color: #2547c9 !important; border: 1px solid #cdd6fb; }
 
/* ---------- ANIMATIONS ---------- */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(24px); }
    to { opacity: 1; transform: translateY(0); }
}
 
hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)
 
 
# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        return "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        return uploaded_file.getvalue().decode("utf-8")
 
 
def score_color(score):
    if score >= 75: return "#16a34a"
    if score >= 50: return "#f59e0b"
    return "#dc2626"
 
 
def donut_chart(value, title):
    """Large circular progress ring — replaces the stock Plotly gauge indicator."""
    color = score_color(value)
    remainder = 100 - value
    fig = go.Figure(data=[go.Pie(
        values=[value, remainder],
        hole=0.78,
        marker=dict(colors=[color, "#eef2fb"], line=dict(width=0)),
        textinfo="none",
        sort=False,
        direction="clockwise",
        rotation=0,
    )])
    fig.update_layout(
        showlegend=False,
        height=230,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[
            dict(text=f"<b>{value:.0f}%</b>", x=0.5, y=0.56, font=dict(size=30, color="#1e293b"), showarrow=False),
            dict(text=title, x=0.5, y=0.38, font=dict(size=12.5, color="#64748b"), showarrow=False),
        ],
    )
    return fig
 
 
def skill_bar_chart(match_count, gap_count, extra_count):
    fig = go.Figure(go.Bar(
        x=[match_count, gap_count, extra_count],
        y=["🟢 Matching", "🔴 Missing", "🔵 Bonus"],
        orientation="h",
        marker_color=["#16a34a", "#dc2626", "#2563eb"],
        text=[match_count, gap_count, extra_count],
        textposition="outside",
        textfont=dict(color="#1e293b", size=13),
    ))
    fig.update_layout(
        height=220, margin=dict(l=10, r=30, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, tickfont={"size": 13, "color": "#1e293b"}),
        font={"color": "#1e293b"},
    )
    return fig
 
 
# ---------------------------------------------------------------------------
# HERO
# ---------------------------------------------------------------------------
st.markdown("""
<div class="hero">
    <div class="hero-badge">🤖 AI-Powered ATS Resume Screening</div>
    <div class="hero-title">Resume Matcher AI</div>
    <div class="hero-sub">Optimize your resume, compare it against any job description, identify
    missing skills, and improve your interview chances — with a fully explainable score.</div>
    <div class="hero-divider"></div>
</div>
""", unsafe_allow_html=True)
 
col1, col2 = st.columns(2, gap="large")
 
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">📄 Resume</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload PDF / DOCX / TXT", type=["pdf", "docx", "txt"], key="resume_upload")
    resume_text = st.text_area("Or paste resume text:", height=250, placeholder="Paste your resume here...", key="resume_text")
    if uploaded_file is not None:
        resume_text = extract_text_from_file(uploaded_file)
        st.success(f"Loaded: {uploaded_file.name}")
    st.markdown('</div>', unsafe_allow_html=True)
 
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">💼 Job Description</div>', unsafe_allow_html=True)
    job_text = st.text_area("Paste job description:", height=306, placeholder="Paste the job description here...", key="job_text")
    st.markdown('</div>', unsafe_allow_html=True)
 
st.markdown("<br>", unsafe_allow_html=True)
_, mid, _ = st.columns([1, 1.2, 1])
with mid:
    analyze = st.button("🚀 Analyze Resume Match", use_container_width=True)
 
if analyze:
    if not resume_text or not resume_text.strip():
        st.error("Please provide a resume (upload a file or paste text).")
    elif not job_text or not job_text.strip():
        st.error("Please provide a job description.")
    else:
        with st.spinner("Analyzing resume against job description..."):
            try:
                results = match_resume_to_job(resume_text, job_text)
            except Exception as e:
                st.error(f"Error during analysis: {e}")
                st.info("Tip: run `python -m spacy download en_core_web_lg` if this is your first run.")
                st.stop()
 
        st.markdown("---")
        st.markdown('<div class="section-label" style="text-align:center; font-size:1rem;">📊 MATCH DASHBOARD</div>', unsafe_allow_html=True)
 
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.plotly_chart(donut_chart(results["overall_score"], "Overall Match"), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with g2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.plotly_chart(donut_chart(results["semantic_score"], "Semantic Score"), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with g3:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.plotly_chart(donut_chart(results["keyword_score"], "ATS Keyword Score"), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
 
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">🧠 AI Explanation</div>', unsafe_allow_html=True)
        st.markdown(results["explanation"])
        st.markdown('</div>', unsafe_allow_html=True)
 
        chart_col, skills_col = st.columns([1, 1.4], gap="large")
 
        with chart_col:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-label">📈 Skills Overview</div>', unsafe_allow_html=True)
            st.plotly_chart(
                skill_bar_chart(results["skill_match_count"], results["skill_gap_count"], len(results["extra_skills"])),
                use_container_width=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)
 
        with skills_col:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-label">🏷️ Skill Breakdown</div>', unsafe_allow_html=True)
 
            st.markdown("**🟢 Matching Skills**")
            if results["matching_skills"]:
                st.markdown("".join(f'<span class="pill pill-match">{s}</span>' for s in results["matching_skills"]), unsafe_allow_html=True)
            else:
                st.caption("No matching skills found.")
 
            st.markdown("<br>**🔴 Missing Skills**", unsafe_allow_html=True)
            if results["missing_skills"]:
                st.markdown("".join(f'<span class="pill pill-missing">{s}</span>' for s in results["missing_skills"]), unsafe_allow_html=True)
            else:
                st.caption("No gaps — nice!")
 
            st.markdown("<br>**🔵 Bonus Skills**", unsafe_allow_html=True)
            if results["extra_skills"]:
                st.markdown("".join(f'<span class="pill pill-extra">{s}</span>' for s in results["extra_skills"]), unsafe_allow_html=True)
            else:
                st.caption("None detected.")
 
            st.markdown('</div>', unsafe_allow_html=True)
 
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">🎓 Experience Analysis</div>', unsafe_allow_html=True)
        exp = results["experience_analysis"]
        e1, e2, e3 = st.columns([1, 1, 1.4])
        with e1:
            st.markdown(f'<div class="metric-tile"><div class="label">👤 Resume Level</div><div class="value" style="color:#2563eb;">{exp["resume_level"].title()}</div></div>', unsafe_allow_html=True)
        with e2:
            st.markdown(f'<div class="metric-tile"><div class="label">🏢 Job Level</div><div class="value" style="color:#2563eb;">{exp["job_level"].title()}</div></div>', unsafe_allow_html=True)
        with e3:
            st.markdown('<div class="metric-tile" style="text-align:left; padding-left:1.4rem;"><div class="label">🎯 Recommendation</div>', unsafe_allow_html=True)
            if exp["match"]:
                st.success("Experience levels align well with this role.")
            else:
                st.warning("There's a seniority gap between your resume and this job.")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
 
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">✅ AI Suggestions</div>', unsafe_allow_html=True)
        recs = []
        if results["missing_skills"]:
            recs.append(f"**Add missing skills** you actually have: {', '.join(results['missing_skills'][:5])}")
        if results["semantic_score"] < 60:
            recs.append("**Improve thematic alignment** — mirror the job's language and emphasis.")
        if results["keyword_score"] < 40:
            recs.append("**Increase keyword density** using exact phrases from the posting.")
        if not exp["match"]:
            recs.append(f"**Highlight {exp['job_level']}-level achievements** to match the role's seniority.")
        if not recs:
            recs.append("Your resume is well aligned with this job. Go ahead and apply! 🚀")
        for r in recs:
            st.markdown(f"✔ {r}")
        st.markdown('</div>', unsafe_allow_html=True)
 
st.markdown("<br><div style='text-align:center; color:#94a3b8; font-size:0.85rem;'>Built with Streamlit · spaCy · Sentence-Transformers · Plotly</div>", unsafe_allow_html=True)
 