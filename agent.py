import os
import requests
from dotenv import load_dotenv

load_dotenv()

OMNIROUTE_URL = "http://localhost:20128/v1/chat/completions"
OMNIROUTE_KEY = os.getenv("OMNIROUTE_KEY")

# Replace this with the exact Combo name you gave your setup in OmniRoute
COMBO_MODEL_NAME = "gemini-fallback"

def ask(question):
    headers = {
        "Authorization": f"Bearer {OMNIROUTE_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": COMBO_MODEL_NAME,
        "messages": [{"role": "user", "content": question}],
        "max_tokens": 150
    }

    try:
        response = requests.post(OMNIROUTE_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        # Check which provider OmniRoute actually routed this request to
        routing_decision = response.headers.get("X-OmniRoute-Decision", "No routing header found")
        print(f"\n[OmniRoute Route]: {routing_decision}")

        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Request failed: {e}"

if __name__ == "__main__":
    while True:
        q = input("\nAsk a question (or 'quit'): ").strip()
        if q.lower() == "quit":
            break
        print(ask(q))