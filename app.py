import streamlit as st
import google.generativeai as genai
import httpx
import xml.etree.ElementTree as ET
from urllib.parse import quote
import json
import re
import asyncio
import time

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="LitSynth — AI Literature Synthesizer",
    page_icon="🔬",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main { background-color: #0a0f0a; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 960px; }

h1 { font-family: 'Inter', sans-serif; font-weight: 700; color: #d4f0e5 !important; }
h2, h3 { color: #9dc9b8 !important; }

.stButton > button {
    background: rgba(0,100,60,0.7) !important;
    color: #00ffc8 !important;
    border: 1px solid rgba(0,255,200,0.4) !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    padding: 0.6rem 1.8rem !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(0,140,80,0.8) !important;
    border-color: rgba(0,255,200,0.7) !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(0,40,25,0.8) !important;
    border: 1px solid rgba(125,211,176,0.25) !important;
    color: #c8e6d9 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
}

.stSlider > div { color: #7dd3b0 !important; }
.stSlider .stSlider { accent-color: #00ffc8; }

.metric-card {
    background: rgba(0,30,20,0.8);
    border: 1px solid rgba(125,211,176,0.2);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #00ffc8;
    font-family: 'IBM Plex Mono', monospace;
}
.metric-label {
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    color: #4a9970;
    text-transform: uppercase;
    font-family: 'IBM Plex Mono', monospace;
}

.cluster-box {
    background: rgba(0,25,15,0.9);
    border: 1px solid rgba(125,211,176,0.15);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}
.cluster-question {
    color: #c8e6d9;
    font-weight: 600;
    font-size: 0.95rem;
    margin-bottom: 0.6rem;
}
.cluster-finding {
    color: #9dc9b8;
    font-size: 0.85rem;
    line-height: 1.7;
}
.cluster-gap {
    color: #f59e0b;
    font-size: 0.78rem;
    margin-top: 0.5rem;
}

.report-box {
    background: linear-gradient(135deg, rgba(0,60,35,0.6), rgba(0,40,25,0.8));
    border: 1px solid rgba(125,211,176,0.3);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
}
.report-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    color: #00ffc8;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}
.report-text {
    color: #d4f0e5;
    font-size: 1rem;
    line-height: 1.8;
    font-style: italic;
}

.tag {
    display: inline-block;
    border-radius: 4px;
    padding: 2px 10px;
    font-size: 0.7rem;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.08em;
    margin-right: 6px;
    text-transform: uppercase;
}
.tag-emerging  { color: #00ffc8; border: 1px solid #00ffc8; }
.tag-active    { color: #4fc3f7; border: 1px solid #4fc3f7; }
.tag-mature    { color: #aaa;    border: 1px solid #aaa; }
.tag-declining { color: #ff6b6b; border: 1px solid #ff6b6b; }
.tag-developing   { color: #4fc3f7; border: 1px solid #4fc3f7; }
.tag-foundational { color: #f9a825; border: 1px solid #f9a825; }
.tag-fragmented   { color: #ff6b6b; border: 1px solid #ff6b6b; }

.paper-card {
    background: rgba(0,15,10,0.7);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
}
.paper-title { color: #7dd3b0; font-weight: 600; font-size: 0.85rem; }
.paper-meta  { color: #4a7060; font-size: 0.72rem; margin: 3px 0 6px; }
.paper-abstract { color: #7a9d8f; font-size: 0.75rem; line-height: 1.6; }

.log-box {
    background: rgba(0,10,6,0.95);
    border: 1px solid rgba(42,107,80,0.4);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: #7dd3b0;
    line-height: 2;
    max-height: 220px;
    overflow-y: auto;
}

.stProgress > div > div > div { background-color: #00ffc8 !important; }

div[data-testid="stMarkdownContainer"] p { color: #9dc9b8; }

hr { border-color: rgba(125,211,176,0.1) !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# AGENT FUNCTIONS
# ─────────────────────────────────────────

def configure_gemini(api_key: str):
    genai.configure(api_key=api_key)

def decompose_topic(topic: str, num_questions: int, model) -> list[str]:
    prompt = f"""You are a research assistant specializing in academic literature analysis.

Given the research topic: "{topic}"

Generate exactly {num_questions} targeted sub-questions that together comprehensively cover this topic.
Each sub-question should:
- Be specific enough to retrieve focused academic papers from arXiv
- Cover a distinct aspect (methods, applications, theory, comparisons, challenges, etc.)
- Be suitable as an arXiv search query

Return ONLY a JSON array of strings, no explanation, no markdown.
Example: ["sub-question 1", "sub-question 2", "sub-question 3"]"""

    response = model.generate_content(prompt)
    text = response.text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        questions = json.loads(text)
        if isinstance(questions, list):
            return [str(q) for q in questions[:num_questions]]
    except Exception:
        pass

    lines = [l.strip().strip('"-,[]') for l in text.split('\n') if l.strip() and l.strip() not in ['[', ']']]
    return [l for l in lines if len(l) > 10][:num_questions]


def fetch_papers(query: str, max_results: int = 5) -> list[dict]:
    ARXIV_API = "https://export.arxiv.org/api/query"
    NS = {"atom": "http://www.w3.org/2005/Atom"}
    url = f"{ARXIV_API}?search_query=all:{quote(query)}&start=0&max_results={max_results}&sortBy=relevance&sortOrder=descending"

    try:
        resp = httpx.get(url, timeout=30)
        resp.raise_for_status()
    except Exception:
        return []

    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError:
        return []

    papers = []
    for entry in root.findall("atom:entry", NS):
        title_el   = entry.find("atom:title", NS)
        summary_el = entry.find("atom:summary", NS)
        id_el      = entry.find("atom:id", NS)
        pub_el     = entry.find("atom:published", NS)

        if title_el is None or summary_el is None:
            continue

        authors = [
            a.find("atom:name", NS).text
            for a in entry.findall("atom:author", NS)
            if a.find("atom:name", NS) is not None
        ]
        cats = [c.attrib.get("term","") for c in entry.findall("atom:category", NS)]
        arxiv_id = (id_el.text or "").split("/abs/")[-1].strip() if id_el is not None else ""

        papers.append({
            "id":       arxiv_id,
            "title":    title_el.text.strip().replace("\n", " "),
            "abstract": summary_el.text.strip().replace("\n", " "),
            "authors":  authors[:5],
            "published": (pub_el.text or "")[:10] if pub_el is not None else "",
            "url":      f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else "",
            "categories": cats[:3],
        })

    return papers


def summarize_cluster(question: str, papers: list[dict], model) -> dict:
    papers_text = ""
    for i, p in enumerate(papers, 1):
        authors = ", ".join(p["authors"][:3]) + (" et al." if len(p["authors"]) > 3 else "")
        papers_text += f"\nPaper {i}: {p['title']}\nAuthors: {authors} ({p['published'][:4] if p['published'] else 'n.d.'})\nAbstract: {p['abstract'][:500]}\n---"

    prompt = f"""You are an expert academic research assistant.

Sub-question: "{question}"

Below are {len(papers)} retrieved arXiv papers:
{papers_text}

Provide a structured analysis. Return ONLY a JSON object with these exact keys:
{{
  "key_findings": "2-3 sentence synthesis of the main findings across these papers",
  "methodologies": "Key methods and approaches used (1-2 sentences)",
  "consensus": "What researchers agree on (1 sentence)",
  "gaps": "Open questions or limitations (1 sentence)",
  "trend": "one of: Emerging | Active | Mature | Declining"
}}

Return ONLY valid JSON, no markdown fences."""

    response = model.generate_content(prompt)
    text = response.text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except Exception:
        return {"key_findings": text[:400], "methodologies": "", "consensus": "", "gaps": "", "trend": "Active"}


def synthesize_report(topic: str, subquestions: list, summaries: dict, all_papers: dict, pro_model) -> dict:
    summary_text = ""
    for q, s in summaries.items():
        summary_text += f"\nSub-question: {q}\nKey findings: {s.get('key_findings','')}\nMethodologies: {s.get('methodologies','')}\nGaps: {s.get('gaps','')}\nTrend: {s.get('trend','')}\n---"

    total = sum(len(v) for v in all_papers.values())

    prompt = f"""You are a senior research analyst writing an executive literature review.

Topic: "{topic}"
Papers analyzed: {total} arXiv papers across {len(subquestions)} sub-questions.

Cluster summaries:
{summary_text}

Write a comprehensive synthesis. Return ONLY a JSON object with these exact keys:
{{
  "executive_summary": "3-4 sentence high-level overview of the field",
  "state_of_the_art": "Current best-performing approach or understanding (2-3 sentences)",
  "major_themes": ["theme 1", "theme 2", "theme 3", "theme 4"],
  "key_challenges": ["challenge 1", "challenge 2", "challenge 3"],
  "future_directions": ["direction 1", "direction 2", "direction 3"],
  "research_maturity": "one of: Foundational | Developing | Mature | Fragmented",
  "recommended_entry_points": "What a new researcher should read first (1-2 sentences)",
  "overall_trend": "1-sentence characterization of how the field is moving"
}}

Return ONLY valid JSON, no markdown fences."""

    response = pro_model.generate_content(prompt)
    text = response.text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except Exception:
        return {
            "executive_summary": text[:500],
            "state_of_the_art": "", "major_themes": [],
            "key_challenges": [], "future_directions": [],
            "research_maturity": "Developing",
            "recommended_entry_points": "", "overall_trend": "",
        }


# ─────────────────────────────────────────
# RENDER HELPERS
# ─────────────────────────────────────────

def trend_tag(label: str) -> str:
    css_class = f"tag-{label.lower()}" if label else "tag-active"
    return f'<span class="tag {css_class}">{label}</span>'


def render_report(report: dict, total_papers: int, num_subquestions: int):
    st.markdown("---")
    st.markdown("### 📋 Synthesis Report")

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{num_subquestions}</div><div class="metric-label">Sub-Questions</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_papers}</div><div class="metric-label">Papers Analyzed</div></div>', unsafe_allow_html=True)
    with col3:
        maturity = report.get("research_maturity", "—")
        color_map = {"Foundational": "#f9a825", "Developing": "#4fc3f7", "Mature": "#aaa", "Fragmented": "#ff6b6b"}
        color = color_map.get(maturity, "#7dd3b0")
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="font-size:1.3rem;color:{color}">{maturity}</div><div class="metric-label">Field Maturity</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="font-size:1.5rem">✓</div><div class="metric-label">Pipeline Done</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Executive summary
    if report.get("executive_summary"):
        st.markdown(f"""
        <div class="report-box">
            <div class="report-label">◆ Executive Summary</div>
            <div class="report-text">{report['executive_summary']}</div>
        </div>""", unsafe_allow_html=True)

    # State of the art + trend
    col_a, col_b = st.columns([2, 1])
    with col_a:
        if report.get("state_of_the_art"):
            st.markdown("**🔬 State of the Art**")
            st.markdown(f"<p style='color:#9dc9b8;font-size:0.9rem;line-height:1.7'>{report['state_of_the_art']}</p>", unsafe_allow_html=True)
    with col_b:
        if report.get("overall_trend"):
            st.markdown("**📈 Overall Trend**")
            st.markdown(f"<p style='color:#7dd3b0;font-size:0.85rem;line-height:1.6;font-style:italic'>{report['overall_trend']}</p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Three columns: themes, challenges, directions
    col1, col2, col3 = st.columns(3)
    sections = [
        ("🧩 Major Themes",      report.get("major_themes", []),      "#4fc3f7"),
        ("⚠️ Key Challenges",    report.get("key_challenges", []),     "#ff6b6b"),
        ("🚀 Future Directions", report.get("future_directions", []),  "#00ffc8"),
    ]
    for col, (title, items, color) in zip([col1, col2, col3], sections):
        with col:
            st.markdown(f"**{title}**")
            for item in items:
                st.markdown(f"<p style='color:#9dc9b8;font-size:0.82rem;line-height:1.5;margin:4px 0'><span style='color:{color}'>→</span> {item}</p>", unsafe_allow_html=True)

    if report.get("recommended_entry_points"):
        st.markdown("<br>", unsafe_allow_html=True)
        st.info(f"📚 **For new researchers:** {report['recommended_entry_points']}")


def render_clusters(subquestions, clusters):
    st.markdown("---")
    st.markdown("### 🔬 Cluster Analysis")

    for i, question in enumerate(subquestions):
        cluster = clusters.get(question, {})
        papers  = cluster.get("papers", [])
        summary = cluster.get("summary")

        if not summary:
            continue

        trend_html = trend_tag(summary.get("trend", "Active"))

        with st.expander(f"Sub-question {i+1}: {question[:80]}{'…' if len(question)>80 else ''}", expanded=False):
            st.markdown(f"{trend_html} &nbsp; <span style='color:#4a9970;font-size:0.75rem'>{len(papers)} papers</span>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            if summary.get("key_findings"):
                st.markdown(f"<p style='color:#9dc9b8;font-size:0.88rem;line-height:1.7'>{summary['key_findings']}</p>", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if summary.get("methodologies"):
                    st.markdown("**Methods**")
                    st.markdown(f"<p style='color:#7a9d8f;font-size:0.8rem;line-height:1.6'>{summary['methodologies']}</p>", unsafe_allow_html=True)
            with c2:
                if summary.get("gaps"):
                    st.markdown("**Open Gaps**")
                    st.markdown(f"<p style='color:#f59e0b;font-size:0.8rem;line-height:1.6'>{summary['gaps']}</p>", unsafe_allow_html=True)

            st.markdown("**Papers Retrieved**")
            for p in papers:
                authors_str = ", ".join(p["authors"][:3]) + (" et al." if len(p["authors"]) > 3 else "")
                year = p["published"][:4] if p["published"] else "n.d."
                cats = " · ".join(p["categories"][:2]) if p["categories"] else ""
                st.markdown(f"""
                <div class="paper-card">
                    <div class="paper-title"><a href="{p['url']}" target="_blank" style="color:#7dd3b0;text-decoration:none">{p['title']}</a></div>
                    <div class="paper-meta">{authors_str} · {year}{' · ' + cats if cats else ''}</div>
                    <div class="paper-abstract">{p['abstract'][:240]}…</div>
                </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────

st.markdown("# 🔬 LitSynth")
st.markdown("<p style='color:#4a9970;font-size:1rem;font-style:italic;margin-top:-8px'>Multi-Agent AI Literature Synthesizer · arXiv + Gemini</p>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar config
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...", help="Get a free key at aistudio.google.com")
    st.markdown("---")
    num_subquestions = st.slider("Sub-questions", min_value=2, max_value=6, value=4, help="How many angles to decompose your topic into")
    papers_per_query = st.slider("Papers per query", min_value=3, max_value=10, value=5, help="arXiv papers retrieved per sub-question")
    st.markdown("---")
    st.markdown("**How it works**")
    st.markdown("""
<p style='font-size:0.78rem;color:#4a9970;line-height:1.8'>
🧩 <b>Decomposer</b> — breaks topic into sub-questions<br>
📡 <b>Retriever</b> — fetches papers from arXiv<br>
🔬 <b>Summarizer</b> — synthesizes each cluster<br>
🧠 <b>Synthesizer</b> — writes the final report
</p>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<p style='font-size:0.72rem;color:#2a6b50'>Built with Gemini 1.5 Flash + Pro · arXiv API · Streamlit</p>", unsafe_allow_html=True)

# Main input
topic = st.text_area(
    "Research Topic",
    placeholder="e.g. Retrieval-Augmented Generation for large language models",
    height=80,
    label_visibility="collapsed",
)

example_cols = st.columns(4)
examples = [
    "RAG for large language models",
    "Diffusion models for medical imaging",
    "Federated learning privacy",
    "Graph neural networks drug discovery",
]
for col, ex in zip(example_cols, examples):
    with col:
        if st.button(ex, key=f"ex_{ex}", use_container_width=True):
            st.session_state["topic_prefill"] = ex
            st.rerun()

if "topic_prefill" in st.session_state:
    topic = st.session_state.pop("topic_prefill")

run_btn = st.button("▶ RUN LITERATURE SYNTHESIS", use_container_width=True)

# ─────────────────────────────────────────
# PIPELINE EXECUTION
# ─────────────────────────────────────────

if run_btn:
    if not topic.strip():
        st.error("Please enter a research topic.")
    elif not api_key.strip():
        st.error("Please enter your Gemini API key in the sidebar.")
    else:
        configure_gemini(api_key)
        flash_model = genai.GenerativeModel("gemini-1.5-flash")
        pro_model   = genai.GenerativeModel("gemini-1.5-pro")

        log_placeholder   = st.empty()
        progress_bar      = st.progress(0)
        status_placeholder = st.empty()

        log_lines = []

        def log(msg: str, icon: str = "⚙️"):
            log_lines.append(f"{icon} {msg}")
            log_placeholder.markdown(
                '<div class="log-box">' + "<br>".join(log_lines[-8:]) + "</div>",
                unsafe_allow_html=True,
            )

        try:
            # Stage 1: Decompose
            log(f'Decomposing "{topic}" into {num_subquestions} sub-questions…', "🧩")
            status_placeholder.info("Stage 1/4 — Decomposing topic...")
            progress_bar.progress(5)

            subquestions = decompose_topic(topic, num_subquestions, flash_model)
            log(f"Generated {len(subquestions)} sub-questions", "✓")
            progress_bar.progress(15)

            # Stage 2: Retrieve
            all_papers = {}
            for i, question in enumerate(subquestions):
                log(f"Retrieving papers: {question[:60]}…", "📡")
                status_placeholder.info(f"Stage 2/4 — Retrieving papers ({i+1}/{len(subquestions)})...")
                papers = fetch_papers(question, max_results=papers_per_query)
                all_papers[question] = papers
                log(f"Found {len(papers)} papers for sub-question {i+1}", "✓")
                progress_bar.progress(15 + int(35 * (i + 1) / len(subquestions)))

            total_papers = sum(len(v) for v in all_papers.values())
            log(f"Total papers retrieved: {total_papers}", "📚")

            # Stage 3: Summarize
            summaries = {}
            for i, (question, papers) in enumerate(all_papers.items()):
                if not papers:
                    continue
                log(f"Summarizing {len(papers)} papers for sub-question {i+1}…", "🔬")
                status_placeholder.info(f"Stage 3/4 — Summarizing clusters ({i+1}/{len(subquestions)})...")
                summary = summarize_cluster(question, papers, flash_model)
                summaries[question] = summary
                log(f"Cluster {i+1} summarized — Trend: {summary.get('trend','?')}", "✓")
                progress_bar.progress(50 + int(30 * (i + 1) / len(subquestions)))

            # Stage 4: Synthesize
            log("Synthesizing final report with Gemini 1.5 Pro…", "🧠")
            status_placeholder.info("Stage 4/4 — Synthesizing final report...")
            progress_bar.progress(85)

            report = synthesize_report(topic, subquestions, summaries, all_papers, pro_model)
            progress_bar.progress(100)

            log("Pipeline complete ✓", "🎉")
            status_placeholder.success(f"✓ Done — {len(subquestions)} sub-questions · {total_papers} papers analyzed")

            # Store results
            st.session_state["result"] = {
                "report": report,
                "subquestions": subquestions,
                "clusters": {q: {"papers": all_papers.get(q, []), "summary": summaries.get(q)} for q in subquestions},
                "total_papers": total_papers,
            }

        except Exception as e:
            st.error(f"Pipeline error: {str(e)}")
            st.stop()

# ─────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────

if "result" in st.session_state:
    res = st.session_state["result"]
    render_report(res["report"], res["total_papers"], len(res["subquestions"]))
    render_clusters(res["subquestions"], res["clusters"])

    # Download JSON report
    st.markdown("---")
    report_json = json.dumps({
        "topic": topic,
        "report": res["report"],
        "subquestions": res["subquestions"],
        "clusters": {
            q: {
                "summary": res["clusters"][q]["summary"],
                "papers": res["clusters"][q]["papers"],
            }
            for q in res["subquestions"]
        }
    }, indent=2)
    st.download_button(
        label="⬇ Download Full Report (JSON)",
        data=report_json,
        file_name=f"litsynth_report_{int(time.time())}.json",
        mime="application/json",
    )
