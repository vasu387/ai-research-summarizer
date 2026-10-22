import os
import requests
from dotenv import load_dotenv

load_dotenv()

OMNIROUTE_URL = "http://localhost:20128/v1/chat/completions"
OMNIROUTE_KEY = os.getenv("OMNIROUTE_KEY")
COMBO_MODEL_NAME = "gemini-fallback"

def get_text_from_url(url: str) -> str:
    try:
        import trafilatura
        downloaded = trafilatura.fetch_url(url)
        return trafilatura.extract(downloaded) or "Could not parse webpage text."
    except Exception as e:
        return f"Error reading URL: {e}"

def get_text_from_pdf(path: str) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        return "\n".join([page.extract_text() or "" for page in reader.pages]).strip() or "Empty PDF."
    except Exception as e:
        return f"Error reading PDF: {e}"

def summarize(content_input: str):
    text = content_input.strip()
    
    if text.startswith("http://") or text.startswith("https://"):
        print("\nFetching text from URL...")
        extracted_content = get_text_from_url(text)
    elif os.path.exists(text) and text.lower().endswith(".pdf"):
        print("\nReading text from PDF...")
        extracted_content = get_text_from_pdf(text)
    else:
        extracted_content = text

    if len(extracted_content) < 20:
        print("\nText is too short to summarize.")
        return

    payload_text = extracted_content[:5000]

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
                    "You are a professional research agent. Summarize the content using this exact format:\n"
                    "1. Executive Summary (2 sentences max)\n"
                    "2. Key Takeaways (3-5 concise bullet points)\n"
                    "3. Core Conclusion"
                )
            },
            {
                "role": "user",
                "content": f"Analyze and summarize this content:\n\n{payload_text}"
            }
        ],
        "max_tokens": 400
    }

    print("\nRouting through OmniRoute fallback engine...")
    try:
        res = requests.post(OMNIROUTE_URL, headers=headers, json=body, timeout=120)
        res.raise_for_status()

        route = res.headers.get("X-OmniRoute-Decision", "Route not reported")
        print(f"[Active Engine]: {route}\n")

        output = res.json()["choices"][0]["message"]["content"]
        print("=" * 50)
        print("                 SUMMARY")
        print("=" * 50)
        print(output)
        print("=" * 50 + "\n")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("\n=== Smart Multi-Source Summarizer Agent ===")
    print("Paste text, a link (https://...), or type 'quit' to exit.\n")

    while True:
        user_input = input("Enter text or URL: ").strip()
        if user_input.lower() == "quit":
            break
        if not user_input:
            continue
        summarize(user_input)