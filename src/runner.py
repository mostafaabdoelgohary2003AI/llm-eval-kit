"""Batch evaluation runner: JSONL in, scored rows + aggregates out."""

from __future__ import annotations

import json
from pathlib import Path

from .judges import HeuristicJudge
from .scorers import TfidfSimilarity

REQUIRED_FIELDS = {"question", "prediction"}


def load_dataset(path: str | Path) -> list[dict]:
    items = []
    for line_no, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        missing = REQUIRED_FIELDS - item.keys()
        if missing:
            raise ValueError(f"{path}:{line_no} missing fields: {sorted(missing)}")
        items.append(item)
    return items


def run_evaluation(dataset_path: str | Path, judge=None) -> dict:
    items = load_dataset(dataset_path)
    if judge is None:
        similarity = TfidfSimilarity().fit(
            [t for item in items for t in (item["prediction"], item.get("reference", ""))]
        )
        judge = HeuristicJudge(similarity)
    rows = []
    for item in items:
        grade = judge.grade(item)
        rows.append({**{k: item[k] for k in ("question", "prediction") if k in item}, **grade})

    scored = [r for r in rows if r["verdict"] != "judge_error"]
    n = max(len(scored), 1)
    aggregates = {
        "items": len(rows),
        "mean_score": round(sum(r["score"] for r in scored) / n, 4),
        "mean_correctness": round(sum(r.get("correctness", 0) for r in scored) / n, 4),
        "mean_groundedness": round(sum(r.get("groundedness", 0) for r in scored) / n, 4),
        "hallucination_rate": round(sum(r["hallucination_flag"] for r in scored) / n, 4),
        "pass_rate": round(sum(r["verdict"] == "pass" for r in scored) / n, 4),
    }
    return {"aggregates": aggregates, "rows": rows}
