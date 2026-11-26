"""Deterministic scorers. No network, no API keys, fully reproducible."""

from __future__ import annotations

import re

_TOKEN = re.compile(r"\w+", re.UNICODE)


def _tokens(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


def exact_match(prediction: str, reference: str) -> float:
    return float(prediction.strip().lower() == reference.strip().lower())


def token_f1(prediction: str, reference: str) -> float:
    """Bag-of-words F1 between prediction and reference."""
    pred, ref = _tokens(prediction), _tokens(reference)
    if not pred or not ref:
        return 0.0
    common = 0
    remaining = ref.copy()
    for tok in pred:
        if tok in remaining:
            remaining.remove(tok)
            common += 1
    if common == 0:
        return 0.0
    precision, recall = common / len(pred), common / len(ref)
    return round(2 * precision * recall / (precision + recall), 4)


def groundedness(prediction: str, context: str) -> float:
    """Share of the prediction's content words that appear in the context.

    A low score means the answer asserts things the source does not say -
    the classic hallucination signature for RAG-style systems.
    """
    if not context.strip():
        return 1.0  # no context supplied: nothing to be ungrounded against
    context_words = {t for t in _tokens(context) if len(t) > 2}
    pred_words = [t for t in _tokens(prediction) if len(t) > 2]
    if not pred_words:
        return 0.0
    covered = sum(1 for t in pred_words if t in context_words)
    return round(covered / len(pred_words), 4)


class TfidfSimilarity:
    """Cosine similarity over TF-IDF vectors, fit once over the eval corpus."""

    def __init__(self) -> None:
        from sklearn.feature_extraction.text import TfidfVectorizer

        self._vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5),
                                           sublinear_tf=True)

    def fit(self, texts: list[str]) -> "TfidfSimilarity":
        self._vectorizer.fit(texts or [""])
        return self

    def similarity(self, a: str, b: str) -> float:
        import numpy as np

        va, vb = self._vectorizer.transform([a, b]).toarray()
        denom = (np.linalg.norm(va) * np.linalg.norm(vb))
        return round(float(va @ vb / denom), 4) if denom else 0.0
