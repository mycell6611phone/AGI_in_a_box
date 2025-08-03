import os
import hashlib
import json
from datetime import datetime

# === CONFIG ===
SEARCH_ROOT = os.path.expanduser("~")  # Full home directory
KEYWORDS = ["loop", "main.py"]
OUTPUT_FILE = os.path.expanduser("~/Desktop/AGI_in_A_box/version_report.json")
MAX_PREVIEW_LINES = 15

def get_file_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def is_candidate(filename):
    return (
        filename == "main.py" or
        filename.lower().startswith("loop") or
        any(keyword in filename.lower() for keyword in KEYWORDS)
    )

def index_versions():
    print(f"[Indexer] Scanning from root: {SEARCH_ROOT}")
    result = []

    for dirpath, _, files in os.walk(SEARCH_ROOT):
        # Skip known system paths
        if any(skip in dirpath for skip in ["/.cache", "/.config", "/.local", "/snap", "/proc", "/sys", "/dev"]):
            continue

        for fname in files:
            if not fname.endswith(".py"):
                continue
            if not is_candidate(fname):
                continue

            full_path = os.path.join(dirpath, fname)
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    preview = ''.join([next(f) for _ in range(MAX_PREVIEW_LINES)])
            except Exception as e:
                preview = f"[Error reading file: {e}]"

            file_stat = os.stat(full_path)
            result.append({
                "file": fname,
                "path": full_path,
                "size": file_stat.st_size,
                "modified": datetime.utcfromtimestamp(file_stat.st_mtime).isoformat(),
                "hash": get_file_hash(full_path),
                "preview": preview
            })

    with open(OUTPUT_FILE, "w") as out:
        json.dump({"version_candidates": result}, out, indent=2)
    print(f"[Indexer] Done. Report saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    index_versions()
