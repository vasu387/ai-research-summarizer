import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

OMNIROUTE_URL = "http://localhost:20128/v1/chat/completions"
OMNIROUTE_KEY = os.getenv("OMNIROUTE_KEY")
COMBO_MODEL_NAME = "gemini-fallback"

st.set_page_config(
    page_title="AI Research Summarizer",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom Design System: Clean Light Aesthetics
st.markdown("""
<style>
    /* 1. Global Page Background & Text */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }

    /* 2. Text Color Overrides */
    h1, h2, h3, h4, h5, h6, p, span, li, strong, em, div {
        color: #0F172A !important;
    }

    /* 3. Hide Unwanted Streamlit Defaults */
    [data-testid="stSidebar"], section[data-testid="stSidebar"], header, footer {
        display: none !important;
    }

    /* 4. Top-Left Brand Title */
    .top-left-brand {
        position: fixed;
        top: 18px;
        left: 28px;
        font-size: 20px;
        font-weight: 700;
        color: #0F172A !important;
        background-color: #FFFFFF;
        z-index: 999;
        display: flex;
        align-items: center;
        gap: 8px;
        letter-spacing: -0.4px;
    }

    /* 5. Center Container Layout */
    .block-container {
        padding-top: 5rem !important;
        padding-bottom: 9rem !important;
        max-width: 820px !important;
        margin: 0 auto;
    }

    /* 6. Chat Bubbles */
    [data-testid="stChatMessage"] {
        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        margin-bottom: 14px !important;
    }
    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] h3, 
    [data-testid="stChatMessage"] li {
        color: #0F172A !important;
    }

    /* 7. Mode Selector Pills */
    div[role="radiogroup"] {
        display: flex !important;
        justify-content: center !important;
        gap: 8px !important;
        background: #F1F5F9 !important;
        padding: 4px !important;
        border-radius: 20px !important;
        width: fit-content !important;
        margin: 0 auto 12px auto !important;
    }
    div[role="radiogroup"] label {
        background: transparent !important;
        border: none !important;
        padding: 6px 16px !important;
        border-radius: 16px !important;
        color: #475569 !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        cursor: pointer !important;
    }
    div[role="radiogroup"] label[data-checked="true"] {
        background: #FFFFFF !important;
        color: #0F172A !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
    }

    /* 8. Bottom Chat Input */
    div[data-testid="stChatInput"] {
        border-radius: 26px !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }

    /* 9. Clean PDF File Uploader */
    div[data-testid="stFileUploader"] section {
        background-color: #FFFFFF !important;
        border: 2px dashed #CBD5E1 !important;
        border-radius: 12px !important;
    }
    div[data-testid="stFileUploader"] button {
        background-color: #F1F5F9 !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# Top Left Brand
st.markdown('<div class="top-left-brand">✨ AI Research Summarizer</div>', unsafe_allow_html=True)

def get_text_from_url(url: str) -> str:
    try:
        import trafilatura
        downloaded = trafilatura.fetch_url(url)
        return trafilatura.extract(downloaded) or "Could not parse webpage text."
    except Exception as e:
        return f"Error reading URL: {e}"

def get_text_from_pdf(uploaded_file) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(uploaded_file)
        return "\n".join([page.extract_text() or "" for page in reader.pages]).strip() or "Empty PDF."
    except Exception as e:
        return f"Error reading PDF: {e}"

def generate_summary(text_payload: str, source_label: str):
    headers = {
        "Authorization": f"Bearer {OMNIROUTE_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": COMBO_MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an executive research agent. Summarize the text using this clean structure:\n"
                    "### 📌 Executive Summary (2 sentences max)\n"
                    "### 💡 Key Takeaways (3 to 5 clear bullet points)\n"
                    "### 🎯 Core Conclusion"
                )
            },
            {
                "role": "user",
                "content": f"Source ({source_label}):\n\n{text_payload[:5000]}"
            }
        ],
        "max_tokens": 450,
        "temperature": 0.2
    }
    response = requests.post(OMNIROUTE_URL, headers=headers, json=body, timeout=120)
    response.raise_for_status()
    route_info = response.headers.get("X-OmniRoute-Decision", "Route not reported")
    result_text = response.json()["choices"][0]["message"]["content"]
    return result_text, route_info

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Hero State
if not st.session_state["chat_history"]:
    st.markdown("""
    <div style="text-align: center; margin-top: 12vh; margin-bottom: 2vh;">
        <h1 style="font-size: 32px; font-weight: 700; color: #0F172A;">Where should we begin?</h1>
        <p style="color: #64748B; font-size: 15px;">Analyze text, web links, or PDF documents with automated model fallback.</p>
    </div>
    """, unsafe_allow_html=True)

# Render Chat History
for message in st.session_state["chat_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "route" in message:
            st.caption(f"⚡ *Engine: `{message['route']}`*")

# Mode Selection Bar
mode = st.radio(
    "Mode",
    options=["✍️ Text", "🌐 Web URL", "📄 PDF Document"],
    horizontal=True,
    label_visibility="collapsed"
)

to_process_text = None
source_tag = ""

if mode == "📄 PDF Document":
    uploaded_pdf = st.file_uploader("Upload PDF document", type=["pdf"], label_visibility="collapsed")
    if uploaded_pdf and st.button("Summarize PDF", type="primary", use_container_width=True):
        with st.spinner("Extracting PDF text..."):
            pdf_text = get_text_from_pdf(uploaded_pdf)
            if len(pdf_text) < 20:
                st.error("The PDF is empty or unreadable.")
            else:
                to_process_text = pdf_text
                source_tag = f"PDF: {uploaded_pdf.name}"
                st.session_state["chat_history"].append({"role": "user", "content": f"📎 Attached PDF: `{uploaded_pdf.name}`"})

elif mode == "🌐 Web URL":
    url_val = st.chat_input("Enter a webpage URL (https://...) and press Enter")
    if url_val:
        clean_url = url_val.strip()
        st.session_state["chat_history"].append({"role": "user", "content": f"🔗 URL: {clean_url}"})
        with st.chat_message("user"):
            st.markdown(f"🔗 URL: {clean_url}")
        with st.spinner("Fetching webpage..."):
            to_process_text = get_text_from_url(clean_url)
            source_tag = f"URL ({clean_url})"

else: # Text Mode
    prompt_val = st.chat_input("Paste text or ask a question and press Enter...")
    if prompt_val:
        raw_text = prompt_val.strip()
        st.session_state["chat_history"].append({"role": "user", "content": raw_text})
        with st.chat_message("user"):
            st.markdown(raw_text)
        to_process_text = raw_text
        source_tag = "Direct Text"

# Execute Agent Summarization
if to_process_text:
    with st.chat_message("assistant"):
        with st.spinner("Analyzing and routing through OmniRoute cascade..."):
            try:
                summary, route = generate_summary(to_process_text, source_tag)
                st.markdown(summary)
                st.caption(f"⚡ *Engine: `{route}`*")
                st.session_state["chat_history"].append({"role": "assistant", "content": summary, "route": route})
            except Exception as e:
                st.error(f"Error: {e}")