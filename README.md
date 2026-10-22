# 📑 AI Research Summarizer Agent

An autonomous research summarization tool powered by an automated multi-provider fallback gateway using **OmniRoute**. The agent ingests direct text, live web URLs, and PDF documents, ensuring zero downtime and rate-limit resilience.

---

## 🚀 Key Features

- Multi-Source Ingestion:
  - ✍️ Direct Text: Clean executive summaries with bullet-point takeaways.
  - 🌐 Web URLs: Autonomous scraping and text cleaning via `trafilatura`.
  - 📄 PDF Documents: Page extraction and analysis via `pypdf`.
- High-Availability Model Fallback:
  - Routes requests through a local OmniRoute proxy (`localhost:20128`).
  - Automated cascade: **Google Gemini** ➡️ **Groq (GPT-OSS / Qwen)** ➡️ **Pollinations**.
  - Dynamic failover protects against API quota depletion (HTTP 429) and upstream provider outages.
- Minimalist Interface: Clean, light-themed chat interface built with Streamlit.

---

## 🛠️ Tech Stack

- Frontend & App State: Streamlit
- Ingestion & Tools: Trafilatura, PyPDF
- Routing & Orchestration: OmniRoute Gateway
- Language Models: Google Gemini, Groq (Llama / Qwen), Pollinations

---

## ⚙️ Quickstart

1. Clone the repository
```bash
git clone [https://github.com/vasu387/ai-research-summarizer.git](https://github.com/vasu387/ai-research-summarizer.git)
cd ai-research-summarizer
