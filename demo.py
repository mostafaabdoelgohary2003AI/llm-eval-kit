"""Evaluate the example dataset offline and write a Markdown report.

Usage:
    python demo.py                 # heuristic judge, fully offline
    LLM_BASE_URL=... LLM_API_KEY=... python demo.py --llm-judge
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.report import render_markdown
from src.runner import run_evaluation


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--llm-judge", action="store_true")
    args = parser.parse_args()

    judge = None
    if args.llm_judge:
        from src.judges import LLMJudge
        from openai_compatible import OpenAICompatibleLLM  # local helper below
        judge = None  # placeholder; see README for wiring your own client

    examples = Path(__file__).parent / "examples"
    result = run_evaluation(examples / "qa_dataset.jsonl", judge=judge)
    report = render_markdown(result)
    (examples / "sample_report.md").write_text(report, encoding="utf-8")

    agg = result["aggregates"]
    print(f"evaluated {agg['items']} items (heuristic judge, offline)")
    for key in ("mean_score", "mean_correctness", "mean_groundedness",
                "hallucination_rate", "pass_rate"):
        print(f"  {key.replace('_', ' '):20} {agg[key]}")
    print("\nper-item:")
    for i, row in enumerate(result["rows"], 1):
        flag = "  <-- hallucination" if row.get("hallucination_flag") else ""
        print(f"  [{i}] {row['verdict']:4} score={row['score']:.2f} "
              f"grounded={row.get('groundedness', 0):.2f} {row['question'][:52]}{flag}")
    print(f"\nreport written to {examples / 'sample_report.md'}")


if __name__ == "__main__":
    main()
