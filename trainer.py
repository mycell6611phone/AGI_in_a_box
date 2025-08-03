import os
import json
import random
from datetime import datetime

TRANSCRIPT_FILE = "gpt_transcripts.jsonl"
ARCHIVE_FILE = "memory_archive.json"
OUTPUT_FILE = "training_data.jsonl"

# === Load Transcripts ===
def load_transcripts():
    print("[Trainer] Loading GPT transcripts...")
    data = []
    with open(TRANSCRIPT_FILE, "r") as f:
        for line in f:
            entry = json.loads(line)
            if entry.get("prompt") and entry.get("response"):
                data.append({
                    "instruction": entry["prompt"].strip(),
                    "response": entry["response"].strip(),
                    "source": "gpt"
                })
    return data

# === Load Memory ===
def load_memory():
    print("[Trainer] Loading archived memory...")
    if not os.path.exists(ARCHIVE_FILE):
        return []
    with open(ARCHIVE_FILE, "r") as f:
        memory = json.load(f)
    entries = []
    for item in memory:
        if item["type"] == "shell":
            entries.append({
                "instruction": f"Execute shell command for: {item['summary']}",
                "response": item["command"],
                "source": "memory"
            })
        elif item["type"] == "file":
            entries.append({
                "instruction": f"Create or patch file '{item['file']}' for: {item['summary']}",
                "response": item["content"],
                "source": "memory"
            })
    return entries

# === Main Conversion ===
def generate_training_data():
    print("[Trainer] Generating training dataset...")
    transcripts = load_transcripts()
    memory_data = load_memory()

    all_data = transcripts + memory_data
    print(f"[Trainer] Loaded {len(all_data)} total examples.")

    # Shuffle + tag
    random.shuffle(all_data)
    for d in all_data:
        d["metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "source": d.pop("source")
        }

    with open(OUTPUT_FILE, "w") as f:
        for item in all_data:
            f.write(json.dumps(item) + "\n")

    print(f"[Trainer] Wrote dataset to: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_training_data()
