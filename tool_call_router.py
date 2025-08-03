import os
import subprocess
from goal_manager   import log_goals, get_goals

# your LocalDocs-backed retrievers
from local_retriever import search_local_files, read_file, search_localdocs

def write_file(filepath: str, content: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(content)
    print(f"[FileWriter] Wrote to {filepath}")

def run_shell(command: str) -> str:
    try:
        output = subprocess.check_output(
            command, shell=True, stderr=subprocess.STDOUT
        )
        return output.decode()
    except subprocess.CalledProcessError as e:
        return f"[ShellError] {e.output.decode()}"

# Registry of all tools your agent can call
AGENT = {
    "write_file":        write_file,
    "run_shell":         run_shell,
    "search_local_files": search_local_files,
    "read_file":         read_file,
    "search_localdocs":  search_localdocs,
    "log_goals":          log_goals,
    "get_goals":         get_goals,
}

