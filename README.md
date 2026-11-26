# llm-eval-kit

An evaluation harness for LLM outputs: deterministic scorers, a heuristic
rubric judge, an optional LLM-as-judge, and Markdown reports. Built to
answer one question honestly — *is this answer actually good, or does it
just sound good?*

![python](https://img.shields.io/badge/python-3.10%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

## Why

LLM features ship on vibes far too often. This kit makes evaluation a
runnable artifact: a labelled dataset (JSONL), one command, and a report
that separates the three failure modes that matter — wrong answers,
ungrounded answers, and confident hallucinations. The hallucination flag
is the point: a low-scoring honest answer is a quality problem, but an
answer that asserts things the source never said is a trust problem.

## What it measures

| metric | source of truth | question it answers |
| --- | --- | --- |
| token F1 | reference answer | does it say the right things? |
| TF-IDF cosine | reference answer | is it the right answer, paraphrased? |
| groundedness | retrieved context | does the source actually support it? |
| hallucination flag | both | does it assert unsupported claims? |

## Quickstart

```bash
pip install -r requirements.txt
python demo.py     # offline, heuristic judge, writes examples/sample_report.md
```

Bring your own data — one JSON object per line:

```json
{"question": "...", "context": "...", "reference": "...", "prediction": "..."}
```

`context` is what the system retrieved (for RAG), `reference` is your
golden answer, `prediction` is what the LLM actually answered.

## What a run looks like (real output, `examples/qa_dataset.jsonl`)

```text
evaluated 5 items (heuristic judge, offline)
  mean score           0.4345
  mean correctness     0.3384
  mean groundedness    0.6327
  hallucination rate   0.2
  pass rate            0.4

per-item:
  [1] pass score=0.62 grounded=0.94 What was Omar's role in FireGuard?
  [2] fail score=0.18 grounded=0.40 What was Omar's role in FireGuard?  <-- hallucination
  [3] fail score=0.35 grounded=0.71 How many charging sessions did the Warsaw project analyse?
  [4] pass score=0.63 grounded=0.53 ما المشكلة التي يحلها RAG؟
  [5] fail score=0.39 grounded=0.57 How many charging sessions did the Warsaw project analyse?
```

Item 2 is a planted hallucination ("trained the YOLO model himself, 99%
accuracy" — the context says his role was deployment). The judge catches
it by triangulating low groundedness against low correctness, which a
similarity-only check would miss.

## Known limitations (stated, not hidden)

- Surface-overlap judges underestimate good paraphrases; that is exactly
  why `LLMJudge` exists as the second tier. Use heuristics for CI,
  LLM-as-judge for release decisions.
- Groundedness is word-level; it will not catch subtly twisted claims.
  Treat the flag as a filter for human review, not a verdict.
- Five items is a demo, not an evaluation. Real sets start at ~100.

## Project structure

```text
src/
  scorers.py   # exact match, token F1, groundedness, TF-IDF similarity
  judges.py    # HeuristicJudge (offline) + LLMJudge (rubric -> JSON)
  runner.py    # JSONL loading, batch scoring, aggregates
  report.py    # Markdown report renderer
examples/
  qa_dataset.jsonl   # 5 items incl. a planted hallucination
  sample_report.md   # real generated report
tests/               # offline pytest suite
```

## Roadmap

- [ ] RAGAS-style faithfulness/answer-relevance decomposition
- [ ] Pairwise A/B comparison mode for prompt iterations
- [ ] CI gate: fail the build when hallucination rate regresses

## Notes

- Developed with AI pair-programming assistance; metric choices and the
  failure-mode taxonomy are my own.
- License: MIT.
