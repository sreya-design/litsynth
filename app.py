import streamlit as st
import google.generativeai as genai
import httpx
import xml.etree.ElementTree as ET
from urllib.parse import quote
import json, re, time

# ──────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="LitSynth — AI Literature Synthesizer",
    page_icon="🔬",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Sora:wght@300;400;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Sora', sans-serif !important; }

.stApp { background: #060d0a !important; }
.block-container { padding: 2rem 2rem 5rem !important; max-width: 1050px !important; }
#MainMenu, footer, header { visibility: hidden; }

.hero-wrap {
    background: linear-gradient(135deg, rgba(0,60,35,0.5) 0%, rgba(0,20,12,0.8) 100%);
    border: 1px solid rgba(0,255,160,0.12);
    border-radius: 20px;
    padding: 2.8rem 3rem 2.4rem;
    margin-bottom: 2rem;
    position: relative; overflow: hidden;
}
.hero-wrap::before {
    content: '';
    position: absolute; top: -80px; right: -80px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(0,255,160,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow { font-family:'IBM Plex Mono',monospace; font-size:0.65rem; letter-spacing:0.22em; color:#00c87a; text-transform:uppercase; margin-bottom:0.7rem; }
.hero-title { font-size:clamp(2rem,4vw,3rem); font-weight:800; color:#e0f5ec; line-height:1.1; margin-bottom:0.7rem; }
.hero-title span { color:#00ffa3; }
.hero-sub { color:#5aad87; font-size:0.95rem; font-weight:300; line-height:1.7; max-width:560px; }
.hero-stats { display:flex; gap:2rem; margin-top:1.6rem; flex-wrap:wrap; }
.hero-stat-val { font-family:'IBM Plex Mono',monospace; font-size:1.5rem; font-weight:600; color:#00ffa3; }
.hero-stat-lbl { font-size:0.68rem; letter-spacing:0.1em; color:#2d7a55; text-transform:uppercase; }

.input-label { font-family:'IBM Plex Mono',monospace; font-size:0.65rem; letter-spacing:0.14em; color:#2d9e63; text-transform:uppercase; margin-bottom:0.5rem; }

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(0,35,20,0.8) !important;
    border: 1px solid rgba(0,255,160,0.18) !important;
    border-radius: 10px !important;
    color: #d0ede0 !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 0.92rem !important;
    padding: 0.7rem 1rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(0,255,160,0.5) !important;
    box-shadow: 0 0 0 3px rgba(0,255,160,0.07) !important;
}
.stTextInput label, .stTextArea label, .stSlider label { color:#3a8c60 !important; font-size:0.78rem !important; }

.stButton > button {
    background: linear-gradient(135deg,#00a86b,#007a4d) !important;
    color: #e0f5ec !important; border: none !important;
    border-radius: 10px !important;
    font-family:'IBM Plex Mono',monospace !important;
    font-size:0.82rem !important; font-weight:600 !important;
    letter-spacing:0.1em !important;
    padding:0.65rem 1.6rem !important; width:100% !important;
    box-shadow:0 4px 20px rgba(0,168,107,0.25) !important;
    transition:all 0.25s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg,#00c880,#009960) !important;
    box-shadow:0 6px 28px rgba(0,200,128,0.35) !important;
    transform:translateY(-1px) !important;
}

div[data-testid="stProgressBar"] > div { background:rgba(0,255,160,0.1) !important; border-radius:99px !important; }
div[data-testid="stProgressBar"] > div > div { background:linear-gradient(90deg,#00a86b,#00ffa3) !important; border-radius:99px !important; }

.metrics-row { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:1.5rem 0; }
.metric-card { background:rgba(0,22,14,0.8); border:1px solid rgba(0,255,160,0.1); border-radius:14px; padding:1.2rem 1rem; text-align:center; }
.metric-val { font-family:'IBM Plex Mono',monospace; font-size:2rem; font-weight:600; color:#00ffa3; line-height:1; margin-bottom:6px; }
.metric-lbl { font-size:0.62rem; letter-spacing:0.12em; color:#1e6640; text-transform:uppercase; }

.report-hero {
    background:linear-gradient(135deg,rgba(0,80,45,0.45),rgba(0,30,18,0.8));
    border:1px solid rgba(0,255,160,0.2); border-radius:18px;
    padding:2.2rem 2.6rem; margin-bottom:1.4rem; position:relative; overflow:hidden;
}
.report-hero::after { content:'◆'; position:absolute; right:2rem; top:1.5rem; font-size:5rem; color:rgba(0,255,160,0.04); pointer-events:none; }
.section-eyebrow { font-family:'IBM Plex Mono',monospace; font-size:0.6rem; letter-spacing:0.2em; color:#00c87a; text-transform:uppercase; margin-bottom:0.7rem; }
.exec-summary { color:#d4ede4; font-size:1.05rem; line-height:1.85; font-weight:300; font-style:italic; }
.trend-banner { background:rgba(0,255,160,0.04); border:1px solid rgba(0,255,160,0.12); border-radius:10px; padding:0.8rem 1.2rem; display:flex; align-items:center; gap:10px; margin-top:1rem; }

.info-card { background:rgba(0,15,10,0.7); border:1px solid rgba(255,255,255,0.06); border-radius:14px; padding:1.4rem 1.2rem; }
.info-card-title { font-family:'IBM Plex Mono',monospace; font-size:0.62rem; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:0.9rem; }
.bullet-item { display:flex; gap:10px; margin-bottom:7px; font-size:0.82rem; line-height:1.5; color:#8abfa8; }
.bullet-arrow { flex-shrink:0; margin-top:1px; }

.log-wrap { background:#030a06; border:1px solid rgba(0,255,160,0.1); border-left:3px solid #00a86b; border-radius:12px; padding:1rem 1.4rem; font-family:'IBM Plex Mono',monospace; font-size:0.76rem; color:#4dbb88; line-height:2.1; max-height:230px; overflow-y:auto; margin-bottom:1.5rem; }
.log-header { font-size:0.6rem; letter-spacing:0.2em; color:#1a5c38; text-transform:uppercase; margin-bottom:0.6rem; border-bottom:1px solid rgba(0,255,160,0.06); padding-bottom:0.4rem; }

.tag { display:inline-block; border-radius:5px; padding:2px 10px; font-size:0.67rem; font-family:'IBM Plex Mono',monospace; font-weight:600; letter-spacing:0.07em; text-transform:uppercase; margin-right:6px; }
.tag-emerging  { color:#00ffa3; border:1px solid #00ffa3; background:rgba(0,255,163,0.05); }
.tag-active    { color:#4fc3f7; border:1px solid #4fc3f7; background:rgba(79,195,247,0.05); }
.tag-mature    { color:#9e9e9e; border:1px solid #9e9e9e; background:rgba(158,158,158,0.05); }
.tag-declining { color:#ff6b6b; border:1px solid #ff6b6b; background:rgba(255,107,107,0.05); }
.tag-developing   { color:#4fc3f7; border:1px solid #4fc3f7; background:rgba(79,195,247,0.05); }
.tag-foundational { color:#ffca28; border:1px solid #ffca28; background:rgba(255,202,40,0.05); }
.tag-fragmented   { color:#ff6b6b; border:1px solid #ff6b6b; background:rgba(255,107,107,0.05); }

.paper-card { background:rgba(0,10,6,0.8); border:1px solid rgba(255,255,255,0.05); border-radius:10px; padding:0.9rem 1.1rem; margin-bottom:8px; }
.paper-card:hover { border-color:rgba(0,255,160,0.15); }
.paper-title { font-weight:600; font-size:0.85rem; }
.paper-meta { color:#2d6645; font-size:0.7rem; margin:4px 0 8px; font-family:'IBM Plex Mono',monospace; }
.paper-abstract { color:#5a8c74; font-size:0.76rem; line-height:1.65; }

div[data-testid="stExpander"] { background:rgba(0,18,11,0.8) !important; border:1px solid rgba(0,255,160,0.1) !important; border-radius:14px !important; margin-bottom:10px !important; }
div[data-testid="stExpander"] summary { color:#8abfa8 !important; font-size:0.88rem !important; font-weight:600 !important; padding:1rem 1.2rem !important; }

section[data-testid="stSidebar"] { background:#040d07 !important; border-right:1px solid rgba(0,255,160,0.07) !important; }
section[data-testid="stSidebar"] .stMarkdown p { color:#3d7a58 !important; font-size:0.8rem !important; }

.stDownloadButton > button { background:transparent !important; border:1px solid rgba(0,255,160,0.25) !important; color:#2d9e63 !important; border-radius:10px !important; font-family:'IBM Plex Mono',monospace !important; font-size:0.78rem !important; width:auto !important; }
.stDownloadButton > button:hover { border-color:rgba(0,255,160,0.5) !important; color:#00ffa3 !important; }

hr { border-color:rgba(0,255,160,0.07) !important; }
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:#0f3d23; border-radius:4px; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────
# HELPERS — get API key from Streamlit Secrets
# ──────────────────────────────────────────────────────
def get_secret_key() -> str:
    try:
        return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        return ""


# ──────────────────────────────────────────────────────
# AGENT FUNCTIONS
# ──────────────────────────────────────────────────────
def decompose_topic(topic, num_q, model):
    prompt = f"""You are a research assistant. Topic: "{topic}"
Generate exactly {num_q} targeted arXiv sub-questions covering distinct aspects (theory, methods, applications, limitations, comparisons).
Return ONLY a JSON array of strings. No markdown."""
    resp = model.generate_content(prompt)
    text = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip())
    try:
        q = json.loads(text)
        if isinstance(q, list):
            return [str(x) for x in q[:num_q]]
    except Exception:
        pass
    lines = [l.strip().strip('"-,[]') for l in text.split('\n') if l.strip() not in ['','[',']']]
    return [l for l in lines if len(l) > 10][:num_q]


def fetch_papers(query, max_results=5):
    NS = {"atom": "http://www.w3.org/2005/Atom"}
    url = f"https://export.arxiv.org/api/query?search_query=all:{quote(query)}&start=0&max_results={max_results}&sortBy=relevance"
    try:
        r = httpx.get(url, timeout=30); r.raise_for_status()
        root = ET.fromstring(r.text)
    except Exception:
        return []
    papers = []
    for e in root.findall("atom:entry", NS):
        t = e.find("atom:title", NS); s = e.find("atom:summary", NS)
        i = e.find("atom:id", NS);    p = e.find("atom:published", NS)
        if t is None or s is None: continue
        authors = [a.find("atom:name", NS).text for a in e.findall("atom:author", NS) if a.find("atom:name", NS) is not None]
        cats    = [c.attrib.get("term","") for c in e.findall("atom:category", NS)]
        aid     = (i.text or "").split("/abs/")[-1].strip() if i is not None else ""
        papers.append({"id":aid, "title":t.text.strip().replace("\n"," "), "abstract":s.text.strip().replace("\n"," "),
                       "authors":authors[:5], "published":(p.text or "")[:10] if p is not None else "",
                       "url":f"https://arxiv.org/abs/{aid}" if aid else "", "categories":cats[:3]})
    return papers


def summarize_cluster(question, papers, model):
    papers_text = ""
    for i, p in enumerate(papers, 1):
        a = ", ".join(p["authors"][:3]) + (" et al." if len(p["authors"])>3 else "")
        papers_text += f"\n[{i}] {p['title']}\n{a} ({p['published'][:4] if p['published'] else 'n.d.'})\n{p['abstract'][:450]}\n---"
    prompt = f"""Academic assistant. Sub-question: "{question}"
{len(papers)} papers:{papers_text}
Return ONLY JSON: {{"key_findings":"2-3 sentence synthesis","methodologies":"key methods","consensus":"what researchers agree on","gaps":"open questions","trend":"Emerging|Active|Mature|Declining"}}"""
    resp = model.generate_content(prompt)
    text = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip())
    try: return json.loads(text)
    except Exception: return {"key_findings":text[:400],"methodologies":"","consensus":"","gaps":"","trend":"Active"}


def synthesize_report(topic, subquestions, summaries, all_papers, model):
    body = ""
    for q, s in summaries.items():
        body += f"\nQ: {q}\nFindings: {s.get('key_findings','')}\nMethods: {s.get('methodologies','')}\nGaps: {s.get('gaps','')}\nTrend: {s.get('trend','')}\n---"
    total = sum(len(v) for v in all_papers.values())
    prompt = f"""Senior research analyst. Topic: "{topic}" · {total} papers · {len(subquestions)} clusters.
{body}
Return ONLY JSON: {{"executive_summary":"3-4 sentence overview","state_of_the_art":"current best approaches","major_themes":["t1","t2","t3","t4"],"key_challenges":["c1","c2","c3"],"future_directions":["d1","d2","d3"],"research_maturity":"Foundational|Developing|Mature|Fragmented","recommended_entry_points":"what to read first","overall_trend":"1-sentence trajectory"}}"""
    resp = model.generate_content(prompt)
    text = re.sub(r"^```json\s*|^```\s*|\s*```$", "", resp.text.strip())
    try: return json.loads(text)
    except Exception: return {"executive_summary":text[:500],"state_of_the_art":"","major_themes":[],"key_challenges":[],"future_directions":[],"research_maturity":"Developing","recommended_entry_points":"","overall_trend":""}


# ──────────────────────────────────────────────────────
# RENDER
# ──────────────────────────────────────────────────────
MATURITY_COLOR = {"Foundational":"#ffca28","Developing":"#4fc3f7","Mature":"#9e9e9e","Fragmented":"#ff6b6b"}

def tag_html(label):
    return f'<span class="tag tag-{label.lower() if label else "active"}">{label}</span>'

def render_report(report, total_papers, num_subq):
    st.markdown("---")
    mc = MATURITY_COLOR.get(report.get("research_maturity",""), "#00ffa3")
    st.markdown(f"""<div class="metrics-row">
        <div class="metric-card"><div class="metric-val">{num_subq}</div><div class="metric-lbl">Sub-Questions</div></div>
        <div class="metric-card"><div class="metric-val">{total_papers}</div><div class="metric-lbl">Papers Analyzed</div></div>
        <div class="metric-card"><div class="metric-val" style="font-size:1.1rem;color:{mc}">{report.get('research_maturity','—')}</div><div class="metric-lbl">Field Maturity</div></div>
        <div class="metric-card"><div class="metric-val">✓</div><div class="metric-lbl">Pipeline Done</div></div>
    </div>""", unsafe_allow_html=True)

    trend_html = f"<div class='trend-banner'><span style='color:#00c87a;font-family:IBM Plex Mono,monospace;font-size:0.68rem;letter-spacing:0.12em'>TREND →</span><span style='color:#8abfa8;font-size:0.85rem;margin-left:8px'>{report.get('overall_trend','')}</span></div>" if report.get('overall_trend') else ""
    st.markdown(f"""<div class="report-hero">
        <div class="section-eyebrow">◆ Executive Summary</div>
        <div class="exec-summary">{report.get('executive_summary','')}</div>
        {trend_html}
    </div>""", unsafe_allow_html=True)

    if report.get("state_of_the_art"):
        c1, c2 = st.columns([3, 2])
        with c1:
            st.markdown(f"""<div class="info-card"><div class="info-card-title" style="color:#2d9e63">🔬 State of the Art</div>
                <p style="color:#8abfa8;font-size:0.88rem;line-height:1.75;margin:0">{report['state_of_the_art']}</p></div>""", unsafe_allow_html=True)
        with c2:
            if report.get("recommended_entry_points"):
                st.markdown(f"""<div class="info-card" style="height:100%"><div class="info-card-title" style="color:#2d6e8a">📚 Start Here</div>
                    <p style="color:#6a9db0;font-size:0.82rem;line-height:1.7;margin:0;font-style:italic">{report['recommended_entry_points']}</p></div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    cols = st.columns(3)
    for col, (key, title, color) in zip(cols, [
        ("major_themes","🧩 Major Themes","#4fc3f7"),
        ("key_challenges","⚠️ Key Challenges","#ff6b6b"),
        ("future_directions","🚀 Future Directions","#00ffa3"),
    ]):
        items = report.get(key, [])
        bullets = "".join(f'<div class="bullet-item"><span class="bullet-arrow" style="color:{color}">→</span>{x}</div>' for x in items)
        with col:
            st.markdown(f"""<div class="info-card"><div class="info-card-title" style="color:{color}">{title}</div>
                {bullets or '<span style="color:#1a4a30;font-size:0.8rem">—</span>'}</div>""", unsafe_allow_html=True)


def render_clusters(subquestions, clusters):
    st.markdown("---")
    st.markdown('<div class="section-eyebrow" style="margin-bottom:1rem">◆ Cluster Analysis</div>', unsafe_allow_html=True)
    for i, q in enumerate(subquestions):
        cluster = clusters.get(q, {}); papers = cluster.get("papers", []); summary = cluster.get("summary")
        if not summary: continue
        with st.expander(f"  {i+1:02d}.  {q[:75]}{'…' if len(q)>75 else ''}", expanded=False):
            st.markdown(f"{tag_html(summary.get('trend','Active'))} &nbsp; <span style='color:#1e6640;font-family:IBM Plex Mono,monospace;font-size:0.72rem'>{len(papers)} papers</span>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if summary.get("key_findings"):
                st.markdown(f"<p style='color:#9dc9b8;font-size:0.88rem;line-height:1.75;margin-bottom:1rem'>{summary['key_findings']}</p>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if summary.get("methodologies"):
                    st.markdown(f"""<div class="info-card"><div class="info-card-title" style="color:#2d9e63">Methods</div>
                        <p style="color:#6aaa88;font-size:0.8rem;line-height:1.65;margin:0">{summary['methodologies']}</p></div>""", unsafe_allow_html=True)
            with c2:
                if summary.get("gaps"):
                    st.markdown(f"""<div class="info-card"><div class="info-card-title" style="color:#c8800a">Open Gaps</div>
                        <p style="color:#c89040;font-size:0.8rem;line-height:1.65;margin:0">{summary['gaps']}</p></div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div style="color:#1a5c38;font-family:IBM Plex Mono,monospace;font-size:0.6rem;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:0.6rem">Retrieved Papers</div>', unsafe_allow_html=True)
            for p in papers:
                a = ", ".join(p["authors"][:3]) + (" et al." if len(p["authors"])>3 else "")
                yr = p["published"][:4] if p["published"] else "n.d."
                cats = " · ".join(p["categories"][:2]) if p["categories"] else ""
                st.markdown(f"""<div class="paper-card">
                    <div class="paper-title"><a href="{p['url']}" target="_blank" style="color:#5aad87;text-decoration:none">{p['title']}</a></div>
                    <div class="paper-meta">{a} · {yr}{' · '+cats if cats else ''} · <a href="{p['url']}" target="_blank" style="color:#1a5c38">arxiv ↗</a></div>
                    <div class="paper-abstract">{p['abstract'][:260]}…</div></div>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="color:#00c87a;font-family:IBM Plex Mono,monospace;font-size:0.62rem;letter-spacing:0.2em;margin-bottom:1.2rem">⚙ CONFIGURATION</div>', unsafe_allow_html=True)

    secret_key = get_secret_key()
    if secret_key:
        st.markdown('<div style="background:rgba(0,255,160,0.06);border:1px solid rgba(0,255,160,0.2);border-radius:8px;padding:8px 12px;color:#2d9e63;font-size:0.75rem;font-family:IBM Plex Mono,monospace;margin-bottom:1rem">✓ API key loaded from Secrets</div>', unsafe_allow_html=True)
        api_key = secret_key
    else:
        st.markdown('<div style="color:#1e5c38;font-size:0.72rem;margin-bottom:4px">Gemini API Key</div>', unsafe_allow_html=True)
        api_key = st.text_input("Gemini API Key", type="password", placeholder="AIza...", label_visibility="collapsed")
        st.markdown('<div style="color:#1a4a2a;font-size:0.68rem;margin-top:4px">Get a free key → <a href="https://aistudio.google.com" target="_blank" style="color:#2d7a55">aistudio.google.com</a></div>', unsafe_allow_html=True)

    st.markdown("---")
    num_subquestions = st.slider("Sub-questions", 2, 6, 4)
    papers_per_query = st.slider("Papers per query", 3, 10, 5)
    st.markdown("---")
    st.markdown("""<div style="color:#1a5c38;font-size:0.75rem;line-height:2.2">
🧩 <b style="color:#2d7a55">Decomposer</b> — sub-questions<br>
📡 <b style="color:#2d7a55">Retriever</b> — arXiv papers<br>
🔬 <b style="color:#2d7a55">Summarizer</b> — cluster analysis<br>
🧠 <b style="color:#2d7a55">Synthesizer</b> — final report
</div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div style="color:#0f3d23;font-size:0.65rem">Gemini 1.5 Flash + Pro · arXiv API · Streamlit</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────
# HERO
# ──────────────────────────────────────────────────────
st.markdown("""<div class="hero-wrap">
    <div class="hero-eyebrow">Multi-Agent AI · arXiv · Google Gemini</div>
    <div class="hero-title">Lit<span>Synth</span></div>
    <div class="hero-sub">Decompose any research topic into targeted sub-questions, retrieve real papers from arXiv, and get a structured executive literature review — automatically.</div>
    <div class="hero-stats">
        <div><div class="hero-stat-val">~5 min</div><div class="hero-stat-lbl">vs 3+ hours manually</div></div>
        <div><div class="hero-stat-val">4</div><div class="hero-stat-lbl">Specialized agents</div></div>
        <div><div class="hero-stat-val">arXiv</div><div class="hero-stat-lbl">Live paper database</div></div>
    </div>
</div>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────
# INPUT
# ──────────────────────────────────────────────────────
st.markdown('<div class="input-label">Research Topic</div>', unsafe_allow_html=True)
topic = st.text_area("Research Topic", placeholder="e.g. Retrieval-Augmented Generation for large language models", height=85, label_visibility="collapsed")

examples = ["RAG for large language models","Diffusion models for medical imaging","Federated learning privacy","Graph neural networks drug discovery"]
cols = st.columns(len(examples))
for col, ex in zip(cols, examples):
    with col:
        if st.button(ex, key=f"ex_{ex}", use_container_width=True):
            st.session_state["prefill"] = ex
            st.rerun()

if "prefill" in st.session_state:
    topic = st.session_state.pop("prefill")

st.markdown("<br>", unsafe_allow_html=True)
run_btn = st.button("▶  RUN LITERATURE SYNTHESIS", use_container_width=True)


# ──────────────────────────────────────────────────────
# PIPELINE
# ──────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.error("Please enter a research topic.")
    elif not api_key.strip():
        st.error("Please add your Gemini API key in the sidebar — or set GEMINI_API_KEY in Streamlit Secrets.")
    else:
        genai.configure(api_key=api_key)
        flash = genai.GenerativeModel("gemini-2.0-flash")
        pro   = genai.GenerativeModel("gemini-2.0-flash")

        log_ph = st.empty(); prog_ph = st.progress(0); status_ph = st.empty()
        log_lines = []

        def log(msg, icon="⚙"):
            log_lines.append(f'<span style="color:#1a5c38">&gt;</span> {icon} {msg}')
            log_ph.markdown(f'<div class="log-wrap"><div class="log-header">Agent Log</div>{"<br>".join(log_lines[-9:])}</div>', unsafe_allow_html=True)

        try:
            log(f'Decomposing "{topic[:55]}…" into {num_subquestions} sub-questions', "🧩")
            status_ph.info("Stage 1 / 4 — Decomposing topic…")
            prog_ph.progress(5)
            subquestions = decompose_topic(topic, num_subquestions, flash)
            log(f"Generated {len(subquestions)} sub-questions ✓", "✓")
            prog_ph.progress(12)

            all_papers = {}
            for i, q in enumerate(subquestions):
                log(f"Fetching papers: {q[:58]}…", "📡")
                status_ph.info(f"Stage 2 / 4 — Retrieving papers ({i+1} / {len(subquestions)})…")
                papers = fetch_papers(q, max_results=papers_per_query)
                all_papers[q] = papers
                log(f"Found {len(papers)} papers for sub-question {i+1} ✓", "✓")
                prog_ph.progress(12 + int(33*(i+1)/len(subquestions)))

            total_papers = sum(len(v) for v in all_papers.values())
            log(f"Total: {total_papers} papers retrieved", "📚")

            summaries = {}
            for i, (q, papers) in enumerate(all_papers.items()):
                if not papers: continue
                log(f"Summarising cluster {i+1} ({len(papers)} papers)…", "🔬")
                status_ph.info(f"Stage 3 / 4 — Summarising clusters ({i+1} / {len(subquestions)})…")
                s = summarize_cluster(q, papers, flash)
                summaries[q] = s
                log(f"Cluster {i+1} done — trend: {s.get('trend','?')} ✓", "✓")
                prog_ph.progress(45 + int(30*(i+1)/len(subquestions)))

            log("Synthesising final report with Gemini 1.5 Pro…", "🧠")
            status_ph.info("Stage 4 / 4 — Writing final synthesis report…")
            prog_ph.progress(85)
            report = synthesize_report(topic, subquestions, summaries, all_papers, pro)
            prog_ph.progress(100)
            log("Pipeline complete 🎉", "🎉")
            status_ph.success(f"✓ Done — {len(subquestions)} sub-questions · {total_papers} papers analyzed")

            st.session_state["result"] = {
                "report": report, "subquestions": subquestions,
                "total_papers": total_papers, "topic": topic,
                "clusters": {q: {"papers": all_papers.get(q,[]), "summary": summaries.get(q)} for q in subquestions},
            }
        except Exception as e:
            st.error(f"Pipeline error: {e}")


# ──────────────────────────────────────────────────────
# RESULTS
# ──────────────────────────────────────────────────────
if "result" in st.session_state:
    r = st.session_state["result"]
    render_report(r["report"], r["total_papers"], len(r["subquestions"]))
    render_clusters(r["subquestions"], r["clusters"])
    st.markdown("---")
    dl_col, _ = st.columns([1, 3])
    with dl_col:
        st.download_button("⬇ Download Report (JSON)",
            data=json.dumps({"topic":r["topic"],"report":r["report"],"subquestions":r["subquestions"],
                             "clusters":{q:{"summary":r["clusters"][q]["summary"],"papers":r["clusters"][q]["papers"]} for q in r["subquestions"]}}, indent=2),
            file_name=f"litsynth_{int(time.time())}.json", mime="application/json")
