import os
import json
import time
import dotenv
import openai
from executor import Executor, execute_plan  # make sure execute_plan is accessible
from memory_recaller import MemoryRecaller

# === LOAD API KEY ===
dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === CONFIG ===
MODEL = "gpt-4"
SYSTEM_PROMPT = """
You are a system planner for an autonomous LLM-based computer. Your job is to:
- Analyze user problems or goals
- Break them into clear shell/file tasks
- Specify: {type: shell/file, content: <command or code>, path: <optional for files>}
- Stop if confirmation is needed
Respond ONLY with a list of JSON objects.
"""

executor = Executor()
recaller = MemoryRecaller()

def ask_gpt_for_plan(user_input):
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
    )
    reply = response.choices[0].message.content
    try:
        return json.loads(reply)
    except json.JSONDecodeError:
        print("[Planner] Failed to parse GPT response:", reply)
        return []

def run_planner(user_input):
    recalled_plan = recaller.recall_plan(user_input)
    if recalled_plan:
        print("[Planner] Recalled plan from memory.")
        execute_plan(recalled_plan)
        return

    print("[Planner] Asking GPT for plan...")
    plan = ask_gpt_for_plan(user_input)
    if plan:
        execute_plan(plan)
    else:
        print("[Planner] GPT did not return a valid plan.")

if __name__ == "__main__":
    print("[GPT Planner] Ready. Type a goal or 'exit':")
    while True:
        user_input = input("\n>> ")
        if user_input.strip().lower() in {"exit", "quit"}:
            break
        run_planner(user_input)
        time.sleep(1)

