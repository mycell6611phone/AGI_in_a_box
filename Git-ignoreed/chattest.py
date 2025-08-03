# experiment_loop.py
"""
Two-Agent Loop Experiment
------------------------
• GPT-4 (OpenAI API) = Planner
• Local LLM (GPT4All-server) = Executor

Features
1. Starts from a user prompt.
2. Maintains sliding memory of the last 3 loop turns.
3. Runs two full GPT→LLM cycles, then pauses:
      press ⏎ (empty input) to keep going,
      or type a new task to pivot.
4. Uses:
      – OPENAI_API_KEY          (env var)
      – local GPT4All HTTP API  (http://localhost:4891)
"""

import os
import sys
import time
import json
import aiohttp
import asyncio
from collections import deque
from dotenv import load_dotenv

load_dotenv()                          # pulls OPENAI_API_KEY

OPENAI_MODEL   = "gpt-4o"
LOCAL_MODEL    = "gpt4all-local"
LOCAL_API_URL  = "http://localhost:4891/v1/chat/completions"
MEMORY_WINDOW  = 3                     # keep last 3 loops
CYCLE_BEFORE_PAUSE = 2                # pause after every 2 loops

# --------------------------------------------------------------------------- #
# Async HTTP helpers
# --------------------------------------------------------------------------- #
async def openai_call(prompt: str) -> str:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    resp = await openai.ChatCompletion.acreate(
        model=OPENAI_MODEL,
        messages=[{"role": "system", "content": "You are the high-level planner."},
                  {"role": "user",    "content": prompt}],
        temperature=0.3
    )
    return resp.choices[0].message.content.strip()

async def local_llm_call(prompt: str) -> str:
    payload = {
        "model": LOCAL_MODEL,
        "messages": [
            {"role": "system", "content": "You are the execution agent."},
            {"role": "user",   "content": prompt}
        ],
        "temperature": 0.5,
        "stream": False
    }
    async with aiohttp.ClientSession() as s:
        async with s.post(LOCAL_API_URL, json=payload) as r:
            data = await r.json()
            return data["choices"][0]["message"]["content"].strip()

# --------------------------------------------------------------------------- #
# Main loop
# --------------------------------------------------------------------------- #
async def run_loop():
    history: deque[str] = deque(maxlen=MEMORY_WINDOW)
    user_task = input("📝 Enter a task for the system:\n> ").strip()
    if not user_task:
        print("No task given. Exiting.")
        return

    cycle = 0
    while True:
        cycle += 1

        # Compose planner prompt with sliding memory
        planner_prompt = (
            f"Task: {user_task}\n\n"
            "Recent context:\n"
            + "\n".join(f"- {h}" for h in history) +
            "\n\nRespond with the next high-level instruction for the executor:"
        )

        gpt_reply = await openai_call(planner_prompt)
        print(f"\n🧠 GPT-4 (planner) says:\n{gpt_reply}\n")

        # Send GPT's instruction to local LLM
        llm_reply = await local_llm_call(gpt_reply)
        print(f"🤖 Local LLM replies:\n{llm_reply}\n")

        # Remember this turn
        history.append(f"GPT: {gpt_reply} | LLM: {llm_reply}")

        # Pause logic
        if cycle % CYCLE_BEFORE_PAUSE == 0:
            user_in = input("⏸  Press ⏎ to continue or type a new task:\n> ").strip()
            if user_in:
                user_task = user_in
                history.clear()
                print("🔄  Task updated. Memory cleared.\n")
            else:
                print("▶️  Continuing...\n")
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        asyncio.run(run_loop())
    except KeyboardInterrupt:
        sys.exit("\nInterrupted by user.")

