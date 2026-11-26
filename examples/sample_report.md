# LLM evaluation report

| metric | value |
| --- | --- |
| items | 5 |
| mean score | 0.4351 |
| mean correctness | 0.3384 |
| mean groundedness | 0.6327 |
| hallucination rate | 0.2 |
| pass rate | 0.4 |

| # | verdict | score | correctness | groundedness | hallucination | question |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | pass | 0.621 | 0.4375 | 0.9444 | no | What was Omar's role in FireGuard? |
| 2 | fail | 0.1838 | 0.08 | 0.4 | yes | What was Omar's role in FireGuard? |
| 3 | fail | 0.3508 | 0.2 | 0.7143 | no | How many charging sessions did the Warsaw project analyse? |
| 4 | pass | 0.6342 | 0.6667 | 0.5333 | no | ما المشكلة التي يحلها RAG؟ |
| 5 | fail | 0.3855 | 0.3077 | 0.5714 | no | How many charging sessions did the Warsaw project analyse? |

Rows flagged for hallucination assert content the source context does
not support. Investigate those first - they are the dangerous failures,
not the low-scoring ones.
