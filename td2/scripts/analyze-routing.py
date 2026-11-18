import csv
import json
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

with (REPO_ROOT / "td1/questions-td1.json").open() as f:
    questions = json.load(f)["questions"]

categories = {q["id"]: q["type"] for q in questions}

files = {
    "A": REPO_ROOT / "td1/traces-A.csv",
    "B": REPO_ROOT / "td1/traces-B.csv",
    "C": REPO_ROOT / "td1/traces-C.csv",
    "D": REPO_ROOT / "td1/traces-D.csv",
    "E": REPO_ROOT / "td1/traces-E.csv",
}

for model, filename in files.items():
    with filename.open(newline="") as f:
        rows = list(csv.DictReader(f))

    # Keep the last attempt for each question.
    final = {}
    for row in rows:
        final[row["case_id"]] = row

    stats = defaultdict(lambda: [0, 0, 0])

    for case, row in final.items():
        category = categories[case]
        stats[category][0] += 1  # Total questions

        if row["verdict"] == "correct":
            stats[category][1] += 1
            stats[category][2] += 1
        elif row["verdict"] != "not_executed":
            stats[category][2] += 1

    print(f"\nMODEL {model}")
    for category, (total, correct, executed) in sorted(stats.items()):
        accuracy = correct / executed * 100 if executed else 0
        print(
            f"{category}: "
            f"{correct}/{executed} executed correct "
            f"({accuracy:.1f}%), "
            f"{total-executed} not executed"
        )
