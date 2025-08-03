import subprocess
import os
import uuid
import json
from datetime import datetime

class Executor:
    """
    Executes shell commands, applies file patches, and logs every action.
    Now with persistent working-directory support.
    """
    def __init__(self, log_dir="execution_logs", dry_run=False):
        self.log_dir = log_dir
        self.dry_run = dry_run
        os.makedirs(log_dir, exist_ok=True)
        self.session_id = str(uuid.uuid4())
        self.log_path = os.path.join(log_dir, f"session_{self.session_id}.json")
        self.log = []
        # start in whatever directory launched this script
        self.cwd = os.getcwd()

    def run_shell(self, command, require_confirm=False):
        if require_confirm:
            print(f"[Executor] Confirm before executing: {command}")
            return {"status": "waiting", "command": command}

        print(f"[Executor] Running in {self.cwd}: {command}")
        # Dry-run: simulate success without touching anything
        if self.dry_run:
            result = {"stdout": "[dry run]", "stderr": "", "code": 0}
        else:
            try:
                # If the user is changing directory, handle that in‐process
                stripped = command.strip()
                if stripped.startswith("cd "):
                    target = stripped[3:].strip()
                    new_dir = os.path.abspath(os.path.join(self.cwd, target))
                    if os.path.isdir(new_dir):
                        self.cwd = new_dir
                        result = {"status": "success", "cwd": self.cwd}
                    else:
                        result = {"status": "error", "message": f"No such directory: {new_dir}"}
                else:
                    # run in the current working directory
                    completed = subprocess.run(
                        command,
                        shell=True,
                        text=True,
                        capture_output=True,
                        cwd=self.cwd
                    )
                    result = {
                        "stdout": completed.stdout,
                        "stderr": completed.stderr,
                        "code": completed.returncode,
                    }
            except Exception as e:
                result = {"stdout": "", "stderr": str(e), "code": -1}

        self._log_action("shell", command, result)
        return result

    def apply_patch(self, filepath, new_content, require_backup=True):
        # interpret relative paths against the current cwd
        full_path = filepath if os.path.isabs(filepath) else os.path.join(self.cwd, filepath)

        if not os.path.exists(full_path):
            return {"status": "error", "message": f"File not found: {full_path}"}

        backup_path = None
        if require_backup:
            backup_path = f"{full_path}.bak.{datetime.now():%Y%m%d%H%M%S}"
            os.rename(full_path, backup_path)

        with open(full_path, "w") as f:
            f.write(new_content)

        self._log_action(
            "file_patch",
            full_path,
            {"backup": backup_path, "status": "success"},
        )
        return {"status": "success", "filepath": full_path}

    def _log_action(self, action_type, target, result):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action_type,
            "target": target,
            "cwd": self.cwd,
            "result": result,
        }
        self.log.append(entry)
        with open(self.log_path, "w") as f:
            json.dump(self.log, f, indent=2)

    def load_log(self):
        if os.path.exists(self.log_path):
            with open(self.log_path, "r") as f:
                return json.load(f)
        return []

def execute_plan(plan):
    """
    Execute a GPT-generated plan: a list of step dicts.
    Each step must have:
      - 'type': either "shell" or "file"
      - if shell: 'content' = the command
      - if file:   'path' or 'target' or 'file' + 'content' = new file contents
    """
    executor = Executor()
    for step in plan:
        t = step.get("type")
        if t == "shell":
            executor.run_shell(step.get("content", ""))
        elif t == "file":
            path = step.get("path") or step.get("target") or step.get("file")
            executor.apply_patch(path, step.get("content", ""))
        else:
            print(f"[execute_plan] Unknown step type: {t!r}, skipping.")

if __name__ == "__main__":
    exe = Executor(dry_run=False)
    exe.run_shell("echo 'Executor is live'")

