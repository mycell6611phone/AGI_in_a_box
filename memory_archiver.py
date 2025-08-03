import os
import json
from datetime import datetime

class MemoryArchiver:
    """
    Stores successful command patterns and their outcomes as reusable memory.
    Prevents redundant GPT calls and enables offline reuse.
    """
    def __init__(self, archive_path="memory_archive.json"):
        self.archive_path = archive_path
        self.memory = self._load_archive()

    def _load_archive(self):
        if os.path.exists(self.archive_path):
            with open(self.archive_path, "r") as f:
                return json.load(f)
        return []

    def archive_successes(self, log):
        for entry in log:
            if entry["action"] == "shell" and entry["result"].get("code", 1) == 0:
                self.memory.append({
                    "type": "shell",
                    "command": entry["target"],
                    "output": entry["result"].get("stdout", "")[:500],
                    "timestamp": entry["timestamp"]
                })
            elif entry["action"] == "file_patch":
                self.memory.append({
                    "type": "file",
                    "file": entry["target"],
                    "timestamp": entry["timestamp"]
                })
        self._save()

    def _save(self):
        with open(self.archive_path, "w") as f:
            json.dump(self.memory, f, indent=2)

    def search_memory(self, query: str):
        results = []
        for mem in self.memory:
            if query.lower() in json.dumps(mem).lower():
                results.append(mem)
        return results

if __name__ == "__main__":
    from feedback_logger import FeedbackLogger
    logger = FeedbackLogger()
    archiver = MemoryArchiver()
    latest_log = logger._load_latest_log()
    archiver.archive_successes(latest_log)
    print("[MemoryArchiver] Archived successful actions.")
