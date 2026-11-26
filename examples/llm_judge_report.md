# LLM evaluation report

| metric | value |
| --- | --- |
| items | 5 |
| mean score | 0.5 |
| mean correctness | 0.4 |
| mean groundedness | 0.6 |
| hallucination rate | 0.4 |
| pass rate | 0.4 |

| # | verdict | score | correctness | groundedness | hallucination | question |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | pass | 1.0 | 1.0 | 1.0 | no | What was Omar's role in FireGuard? |
| 2 | fail | 0.0 | 0.0 | 0.0 | yes | What was Omar's role in FireGuard? |
| 3 | fail | 0.5 | 0.0 | 1.0 | no | How many charging sessions did the Warsaw project analyse? |
| 4 | pass | 1.0 | 1.0 | 1.0 | no | ما المشكلة التي يحلها RAG؟ |
| 5 | fail | 0.0 | 0.0 | 0.0 | yes | How many charging sessions did the Warsaw project analyse? |

Rows flagged for hallucination assert content the source context does
not support. Investigate those first - they are the dangerous failures,
not the low-scoring ones.
