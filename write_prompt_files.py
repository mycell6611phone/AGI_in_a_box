# write_prompt_files.py

from tool_call_router import write_file
import os

PROMPT_DIR = "./prompts"

PROMPTS = {
    "core_loop.txt": """You are building the core_loop module for a modular AGI system.

Purpose:
Orchestrates the full cognition cycle of the AGI system.

Requirements:
- Calls all submodules in sequence: perceive → recall → think → critique → decide → execute → reflect → remember → improve.
- Handles loop timing, error logging, and state transitions.
- Must integrate with: memory, planner, critic, executor, goal manager.

Output ONLY valid Python code.
Begin now.
""",
    "memory.txt": """You are building the memory module for a modular AGI system.

Purpose:
Provides vector memory using FAISS and metadata storage via SQLite or JSON.

Requirements:
- Methods: insert, search (semantic), update, delete, size, fetch_all
- Must support similarity search via sentence-transformers
- Metadata includes: timestamp, tags, certainty, importance, recall count

Output only working Python code.
""",
    "goal_manager.txt": """You are building the goal_manager module for a modular AGI system.

Purpose:
Track and manage high-level goals submitted to the AGI.

Requirements:
- Add, update, complete, remove, and list goals
- Track metadata: status, attempts, timestamps
- Use unique goal IDs

Output only Python code – no explanations.
""",
    # Add more prompt definitions here, or I will stream them to you below to paste in
}

def main():
    os.makedirs(PROMPT_DIR, exist_ok=True)
    for filename, content in PROMPTS.items():
        filepath = os.path.join(PROMPT_DIR, filename)
        write_file(filepath, content)
    print("[Writer] All prompt files written.")

if __name__ == "__main__":
    main()

