import aiohttp

API_URL = "http://localhost:4891/v1/chat/completions"

async def call_local_model(prompt: str, model: str = "llama3:8b") -> str:
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "stream": False
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, headers=headers, json=payload) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Local LLM error {resp.status}: {await resp.text()}")
            result = await resp.json()
            return result["choices"][0]["message"]["content"]
