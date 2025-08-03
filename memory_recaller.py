import os
import json
import time
import dotenv
import openai
from executor import Executor, execute_plan  # now valid

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

class MemoryRecaller:
    """
    Placeholder for memory-based plan recall.
    Replace recall_plan() with your vector-search or DB lookup logic.
    """
    def recall_plan(self, user_input: str):
        # TODO: implement semantic search over past plans
        return None

executor = Executor()
recaller = MemoryRecaller()
LOG_FILE = "gpt_transcripts.jsonl"

def log_gpt_interaction(prompt, raw_response):
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "prompt": prompt,
        "response": raw_response
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def ask_gpt_for_plan(user_input):
    print("[Planner] Sending prompt to GPT...")
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_input}
        ]
    )
    reply = response.choices[0].message.content
    log_gpt_interaction(user_input, reply)

    try:
        plan = json.loads(reply)
        print(f"[Planner] GPT returned {len(plan)} steps.")
        return plan
    except json.JSONDecodeError:
        print("[Planner] Failed to parse GPT response:", reply)
        return []

def run_planner(user_input):
    print("[Planner] Checking memory recall first...")
    recalled_plan = recaller.recall_plan(user_input)
    if recalled_plan:
        print(f"[Planner] Recalled {len(recalled_plan)} steps from memory.")
        execute_plan(recalled_plan)
        return

    print("[Planner] No memory match found.")
    confirm = input("Use GPT to plan? [y/N]: ").strip().lower()
    if confirm != "y":
        print("[Planner] Skipping GPT call.")
        return

    plan = ask_gpt_for_plan(user_input)
    if plan:
        print("[Planner] Executing GPT-generated plan...")
        execute_plan(plan)
    else:
        print("[Planner] GPT did not return a valid plan.")

if __name__ == "__main__":
    print("[GPT Planner] System ready. Enter a task description or type 'exit'.")
    while True:
        user_input = input("\n>> ")
        if user_input.strip().lower() in {"exit", "quit"}:
            print("[Planner] Exiting.")
            break
        run_planner(user_input)
        print("[Planner] Cycle complete.")
        time.sleep(1)

