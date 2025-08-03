import os
import json
from llm_client import call_local_model

BASE_DIR = os.path.expanduser("~/Desktop/AGI_in_A_box_v2/legacy_modules")

def search_local_files(query: str, top_k: int = 5) -> str:
    """
    1) Walk BASE_DIR and list all file paths.
    2) Ask the local LLM to rank the most relevant files for `query`.
    3) Read those top_k files and return a JSON blob: { path: content }.
    """
    # 1) gather file list
    all_files = []
    for root, _, files in os.walk(BASE_DIR):
        for fn in files:
            all_files.append(os.path.relpath(os.path.join(root, fn), BASE_DIR))

    # 2) prompt local LLM to pick top_k
    prompt = {
        "role": "system",
        "content": (
            "You are a file-retrieval assistant. "
            f"Given the user query: “{query}”, rank the following files "
            "in order of relevance, and output a JSON list of the top "
            f"{top_k} file paths. List only paths, nothing else.\n\n"
            + "\n".join(all_files)
        )
    }
    resp = call_local_model([prompt])
    try:
        candidates = json.loads(resp)
        if not isinstance(candidates, list):
            raise ValueError
    except Exception:
        candidates = all_files[:top_k]

    # 3) read and return contents
    result = {}
    for path in candidates:
        full = os.path.join(BASE_DIR, path)
        try:
            with open(full, "r") as f:
                result[path] = f.read()
        except Exception as e:
            result[path] = f"[ERROR reading file: {e}]"

    return json.dumps(result, indent=2)

def read_file(path: str) -> str:
    """
    Return the raw contents of a file under BASE_DIR.
    """
    full = path if os.path.isabs(path) else os.path.join(BASE_DIR, path)
    if not os.path.exists(full):
        return f"[ERROR] File not found: {path}"
    with open(full, "r") as f:
        return f.read()

def search_localdocs(query: str) -> str:
    """
    Use GPT4All’s built-in LocalDocs index to fetch
    relevant snippets for `query`.
    """
    messages = [
        {"role": "system", "content": (
            "You have access to a LocalDocs index of the entire codebase. "
            "Given the user query, return the most relevant file snippets "
            "or document excerpts, in plain text (no JSON)."
        )},
        {"role": "user", "content": query}
    ]
    return call_local_model(messages)

