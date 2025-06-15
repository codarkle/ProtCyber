import os
import json
import requests

API_KEY = os.getenv("PERPLEXITY_API_KEY")
MODEL = "llama-3-8b-instruct"  # or another model Perplexity offers
API_URL = "https://api.perplexity.ai/chat/completions"  # Replace with actual endpoint

def get_processed_info(data):
    prompt = (
        f"You are a cybersecurity expert. For the following web vulnerability:\n\n"
        f"data: {data}\n\n"
        f"Provide the following:\n"
        f"1. Category (e.g., Injection, XSS, etc.)\n"
        f"2. Description (max 500 characters)\n"
        f"3. Recommendation (max 500 characters)\n"
        f"4. Classification (e.g., CVE ID or OWASP category)\n\n"
        f"Format response in strict JSON with keys: category, description, recommendation, classification."
    )
    
    if not API_KEY:
        print("[ERROR] PERPLEXITY_API_KEY is not set!")
        return {}

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        message = result["choices"][0]["message"]["content"]
        return json.loads(message)

    except Exception as e:
        # num = num + 1
        print(f"Error calling Perplexity API: {e}")
        return {}
