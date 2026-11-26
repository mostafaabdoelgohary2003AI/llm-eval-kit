"""Render an evaluation result as a Markdown report."""

from __future__ import annotations


def render_markdown(result: dict, title: str = "LLM evaluation report") -> str:
    agg = result["aggregates"]
    lines = [
        f"# {title}",
        "",
        "| metric | value |",
        "| --- | --- |",
        f"| items | {agg['items']} |",
        f"| mean score | {agg['mean_score']} |",
        f"| mean correctness | {agg['mean_correctness']} |",
        f"| mean groundedness | {agg['mean_groundedness']} |",
        f"| hallucination rate | {agg['hallucination_rate']} |",
        f"| pass rate | {agg['pass_rate']} |",
        "",
        "| # | verdict | score | correctness | groundedness | hallucination | question |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for i, row in enumerate(result["rows"], 1):
        question = row["question"].replace("|", "\\|")[:60]
        flag = "yes" if row.get("hallucination_flag") else "no"
        lines.append(
            f"| {i} | {row['verdict']} | {row['score']} | "
            f"{row.get('correctness', '-')} | {row.get('groundedness', '-')} | "
            f"{flag} | {question} |"
        )
    lines += [
        "",
        "Rows flagged for hallucination assert content the source context does",
        "not support. Investigate those first - they are the dangerous failures,",
        "not the low-scoring ones.",
    ]
    return "\n".join(lines) + "\n"
