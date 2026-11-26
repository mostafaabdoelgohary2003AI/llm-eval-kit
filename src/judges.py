"""Judges combine scorers into a verdict.

``HeuristicJudge`` is deterministic and offline. ``LLMJudge`` asks an
OpenAI-compatible model to grade against a rubric and parses the JSON it
returns (with a safe fallback when the model misbehaves).
"""

from __future__ import annotations

import json

from .scorers import TfidfSimilarity, groundedness, token_f1


class HeuristicJudge:
    """Rubric: correctness (vs reference), groundedness (vs context)."""

    def __init__(self, similarity: TfidfSimilarity | None = None) -> None:
        self.similarity = similarity or TfidfSimilarity()

    def grade(self, item: dict) -> dict:
        prediction = item["prediction"]
        reference = item.get("reference", "")
        context = item.get("context", "")
        correctness = token_f1(prediction, reference)
        semantic = self.similarity.similarity(prediction, reference)
        grounded = groundedness(prediction, context)
        hallucinated = grounded < 0.5 and correctness < 0.3
        score = round(0.45 * correctness + 0.25 * semantic + 0.30 * grounded, 4)
        return {
            "correctness": correctness,
            "semantic_similarity": semantic,
            "groundedness": grounded,
            "hallucination_flag": hallucinated,
            "score": score,
            "verdict": "pass" if score >= 0.6 and not hallucinated else "fail",
        }


class LLMJudge:
    """LLM-as-judge with a rubric prompt and robust JSON parsing."""

    RUBRIC = (
        "Grade the PREDICTION against the REFERENCE answer, using the CONTEXT "
        "as the only source of truth. Reply with a single JSON object: "
        '{"correctness": 0-1, "groundedness": 0-1, "hallucination": true/false, '
        '"reason": "one sentence"}'
    )

    def __init__(self, llm) -> None:
        self.llm = llm  # any client with .complete(system, user) -> str

    def grade(self, item: dict) -> dict:
        user = (
            f"CONTEXT:\n{item.get('context', '(none)')}\n\n"
            f"QUESTION:\n{item['question']}\n\n"
            f"REFERENCE:\n{item.get('reference', '(none)')}\n\n"
            f"PREDICTION:\n{item['prediction']}"
        )
        try:
            raw = self.llm.complete(self.RUBRIC, user)
            start, end = raw.find("{"), raw.rfind("}")
            parsed = json.loads(raw[start : end + 1])
            correctness = float(parsed.get("correctness", 0))
            grounded = float(parsed.get("groundedness", 0))
            hallucinated = bool(parsed.get("hallucination", False))
            score = round(0.5 * correctness + 0.5 * grounded, 4)
            return {
                "correctness": correctness,
                "groundedness": grounded,
                "hallucination_flag": hallucinated,
                "score": score,
                "verdict": "pass" if score >= 0.6 and not hallucinated else "fail",
                "judge_reason": str(parsed.get("reason", ""))[:300],
            }
        except Exception as exc:  # a judge failure must not kill the run
            return {"score": 0.0, "verdict": "judge_error", "judge_reason": str(exc)[:200]}
