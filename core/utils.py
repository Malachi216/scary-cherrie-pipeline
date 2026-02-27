# core/utils.py
import os, json, time

RUNS_DIR = "runs"

def ensure_run_dir(run_id: str):
    os.makedirs(RUNS_DIR, exist_ok=True)
    os.makedirs(os.path.join(RUNS_DIR, run_id), exist_ok=True)

def get_or_create_run_id(current_run_id: str | None) -> str:
    if current_run_id:
        return current_run_id
    return f"run_{int(time.time())}"

def save_json(run_id: str, filename: str, data):
    ensure_run_dir(run_id)
    path = os.path.join(RUNS_DIR, run_id, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def word_count(text: str) -> int:
    return len([w for w in text.split() if w.strip()])
