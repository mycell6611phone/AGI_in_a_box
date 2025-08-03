import os
from datetime import datetime
import uuid

# === CONFIG ===
LOCALDOCS_PATH = "/home/sentinel/.var/app/io.gpt4all.gpt4all/data/nomic.ai/GPT4All/docs"

def sanitize_filename(text: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in text.lower())

def store_memory(role: str, content: str, tags=None):
    tags = tags or []
    timestamp = datetime.utcnow().isoformat()
    entry_id = str(uuid.uuid4())[:8]
    tag_str = ", ".join(tags)
    
    filename = f"{timestamp[:10]}_{sanitize_filename(role)}_{entry_id}.md"
    full_path = os.path.join(LOCALDOCS_PATH, filename)
    
    memory_block = f"""# Memory Entry ({entry_id})
**Role:** {role}  
**Timestamp:** {timestamp}  
**Tags:** {tag_str}  

---

{content}
"""

    with open(full_path, "w") as f:
        f.write(memory_block)
    
    print(f"[MemoryLogger] Stored memory: {filename}")
    return full_path

def mark_for_reindex():
    print("[MemoryLogger] Reindex manually in GPT4All GUI or add CLI hook here.")

# === EXAMPLE USAGE ===
if __name__ == "__main__":
    store_memory("agent", "System initialized. AGI handoff to local LLMs begun.", tags=["agi", "init"])
