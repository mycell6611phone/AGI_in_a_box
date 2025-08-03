import os
import json
from datetime import datetime

class FeedbackLogger:
    """
    Monitors executor logs and generates plain-English summaries.
    Can be used to feed result summaries back to GPT or display to user.
    """
    def __init__(self, log_dir="execution_logs"):
        self.log_dir = log_dir

    def _load_latest_log(self):
        logs = [f for f in os.listdir(self.log_dir) if f.endswith(".json")]
        if not logs:
            return []
        latest = max(logs, key=lambda x: os.path.getmtime(os.path.join(self.log_dir, x)))
        with open(os.path.join(self.log_dir, latest), "r") as f:
            return json.load(f)

    def summarize(self, last_n=5):
        entries = self._load_latest_log()[-last_n:]
        summary = []
        for entry in entries:
            action = entry["action"]
            target = entry["target"]
            result = entry["result"]

            if action == "shell":
                line = f"Ran shell command: '{target}' → Exit code {result['code']}"
                if result['stderr']:
                    line += f" | Error: {result['stderr'].strip()}"
                else:
                    line += f" | Output: {result['stdout'].strip()}"

            elif action == "file_patch":
                line = f"Patched file '{target}'"
                if result.get("backup"):
                    line += f" (backup created at {result['backup']})"

            else:
                line = f"Unknown action type: {action}"

            summary.append(line)
        return summary

if __name__ == "__main__":
    logger = FeedbackLogger()
    report = logger.summarize()
    print("\n[Feedback Summary]")
    for line in report:
        print("-", line)
