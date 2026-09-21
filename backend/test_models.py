import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

async def discover_all_models():
    async with httpx.AsyncClient(timeout=15.0) as client:
        # 1. Groq models
        resp = await client.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {groq_key}"}
        )
        if resp.status_code == 200:
            groq_models = [m["id"] for m in resp.json().get("data", [])]
            print("ALL Groq Models in account:")
            for m in sorted(groq_models):
                print("  -", m)
                
            # Try chat completion on candidate models
            for test_m in groq_models:
                if "whisper" in test_m or "guard" in test_m:
                    continue
                chat = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {groq_key}"},
                    json={
                        "model": test_m,
                        "messages": [{"role": "user", "content": "Hello, answer in 5 words."}],
                        "max_tokens": 20
                    }
                )
                print(f"Chat test with '{test_m}': status={chat.status_code}")
                if chat.status_code == 200:
                    ans = chat.json()["choices"][0]["message"]["content"]
                    print(f"  >>> SUCCESS: {ans.strip()}")
        
        # 2. Gemini models
        gemini_models_resp = await client.get(
            f"https://generativelanguage.googleapis.com/v1beta/models?key={gemini_key}"
        )
        print(f"\nGemini list models status: {gemini_models_resp.status_code}")
        if gemini_models_resp.status_code == 200:
            g_models = [m["name"] for m in gemini_models_resp.json().get("models", [])]
            print("Available Gemini models:")
            for gm in g_models[:15]:
                print("  -", gm)

if __name__ == "__main__":
    asyncio.run(discover_all_models())
