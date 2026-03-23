# 🔬 LitSynth — Multi-Agent AI Literature Synthesizer

> Turn any research topic into a structured literature review in under 5 minutes.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)

## What it does

LitSynth uses a **4-agent pipeline** powered by Google Gemini and the arXiv API to automatically:

1. **Decompose** your topic into 3–5 targeted sub-questions
2. **Retrieve** 5–10 real academic papers per sub-question from arXiv
3. **Summarize** each paper cluster (key findings, methods, gaps, trend)
4. **Synthesize** a final executive report with themes, challenges, and future directions

Reduces literature review time from ~3 hours → under 5 minutes.

## Tech Stack

`Python` · `Streamlit` · `Google Gemini API` · `arXiv API` · `Prompt Engineering` · `Multi-Agent Design`

## Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/litsynth.git
cd litsynth
pip install -r requirements.txt
streamlit run app.py
```

Add your Gemini API key in the sidebar when the app opens.


## Project Structure

```
litsynth/
├── app.py               # Full single-file Streamlit app
├── requirements.txt     # Python dependencies
├── .streamlit/
│   └── config.toml      # Theme configuration
└── README.md
```

## Agent Architecture

```
User Input (topic)
       │
       ▼
┌─────────────────┐
│ DecomposerAgent │  Gemini 1.5 Flash → 3–5 sub-questions
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  RetrieverAgent │  arXiv API → papers per sub-question
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SummarizerAgent │  Gemini 1.5 Flash → cluster summaries
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│ SynthesizerAgent │  Gemini 1.5 Pro → final report
└──────────────────┘
```

## Get a Free Gemini API Key

→ [aistudio.google.com](https://aistudio.google.com) — free tier is sufficient

## License

MIT
