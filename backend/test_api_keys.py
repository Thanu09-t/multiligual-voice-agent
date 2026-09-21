import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

async def test_groq():
    print(f"Testing Groq key: {groq_key[:10]}...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test Groq models
        try:
            resp = await client.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {groq_key}"}
            )
            print(f"Groq Models Status: {resp.status_code}")
            if resp.status_code == 200:
                models = [m["id"] for m in resp.json().get("data", [])]
                print("Available Groq models:", [m for m in models if "llama" in m or "whisper" in m or "qwen" in m][:8])
                
                # Test chat completion with llama-3.3-70b-versatile
                chat_resp = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {groq_key}"},
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": "Respond with 'Groq online and accurate!'"}]
                    }
                )
                print(f"Groq Chat Status: {chat_resp.status_code}")
                if chat_resp.status_code == 200:
                    print("Groq Chat Response:", chat_resp.json()["choices"][0]["message"]["content"])
                else:
                    print("Groq Chat Error:", chat_resp.text)
            else:
                print("Groq Error:", resp.text)
        except Exception as e:
            print("Groq Exception:", e)

async def test_gemini():
    print(f"\nTesting Gemini key: {gemini_key[:10]}...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        for model in ["gemini-1.5-flash", "gemini-2.5-flash", "gemini-2.0-flash"]:
            try:
                resp = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}",
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{"role": "user", "parts": [{"text": "Say 'Gemini active!'"}]}]
                    }
                )
                print(f"Gemini {model} Status: {resp.status_code}")
                if resp.status_code == 200:
                    text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"Gemini {model} Response: {text.strip()}")
                    break
                else:
                    print(f"Gemini {model} Error: {resp.text[:120]}")
            except Exception as e:
                print(f"Gemini {model} Exception:", e)

async def main():
    await test_groq()
    await test_gemini()

if __name__ == "__main__":
    asyncio.run(main())
