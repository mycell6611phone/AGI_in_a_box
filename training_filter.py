import json
import os
from datetime import datetime
from local_llm import call_local_model

INPUT_FILE = "training_data.jsonl"
OUTPUT_FILE = "scored_training_data.jsonl"

def score_example(example):
    prompt = f"""
Evaluate the following instruction-response pair for quality:

Instruction:
{example['instruction']}

Response:
{example['response']}

Score from 1 to 10 based on correctness, clarity, and usefulness. Just return the number.
"""
    reply = call_local_model(prompt)
    try:
        score = int(''.join(c for c in reply if c.isdigit()))
        return min(max(score, 1), 10)
    except:
        return 1

def rank_and_filter_data(input_path, output_path, min_score=6):
    print(f"[Filter] Reading: {input_path}")
    passed, skipped = 0, 0
    with open(input_path, "r") as infile, open(output_path, "w") as outfile:
        for line in infile:
            example = json.loads(line)
            score = score_example(example)
            example["score"] = score
            example["metadata"]["scored_at"] = datetime.now().isoformat()
            if score >= min_score:
                outfile.write(json.dumps(example) + "\n")
                passed += 1
            else:
                skipped += 1
    print(f"[Filter] Saved {passed} high-quality examples, skipped {skipped}.")

if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        print("[Error] Input file not found.")
    else:
        rank_and_filter_data(INPUT_FILE, OUTPUT_FILE)
