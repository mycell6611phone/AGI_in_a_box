import os
import json
from executor import Executor
from gpt_planner import ask_gpt_for_plan, execute_plan
from feedback_logger import FeedbackLogger

class RetryHandler:
    """
    Scans latest executor logs for failed commands and triggers retry plans.
    If GPT is used, failed commands are sent back with context.
    """
    def __init__(self, log_dir="execution_logs"):
        self.executor = Executor()
        self.logger = FeedbackLogger(log_dir=log_dir)
        self.log_dir = log_dir

    def _load_latest_log(self):
        logs = [f for f in os.listdir(self.log_dir) if f.endswith(".json")]
        if not logs:
            return []
        latest = max(logs, key=lambda x: os.path.getmtime(os.path.join(self.log_dir, x)))
        with open(os.path.join(self.log_dir, latest), "r") as f:
            return json.load(f)

    def find_failures(self):
        log = self._load_latest_log()
        failures = []
        for entry in log:
            result = entry.get("result", {})
            if result.get("code", 0) != 0 or result.get("status") == "error":
                failures.append(entry)
        return failures

    def retry_failed(self):
        failures = self.find_failures()
        if not failures:
            print("[RetryHandler] No failed steps found.")
            return

        print(f"[RetryHandler] Found {len(failures)} failed steps. Asking GPT to recover...")

        # Create a GPT prompt with error context
        prompt = "The following system steps failed. Create a corrected plan:\n"
        for fail in failures:
            prompt += f"\n[{fail['action'].upper()}] {fail['target']}\nERROR: {fail['result'].get('stderr') or fail['result']}\n"

        new_plan = ask_gpt_for_plan(prompt)
        if new_plan:
            print("[RetryHandler] Executing recovery steps...")
            execute_plan(new_plan)
        else:
            print("[RetryHandler] GPT did not return a recovery plan.")

if __name__ == "__main__":
    handler = RetryHandler()
    handler.retry_failed()
