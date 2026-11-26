import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.judges import HeuristicJudge
from src.runner import run_evaluation
from src.scorers import TfidfSimilarity, groundedness, token_f1

BASE = Path(__file__).resolve().parents[1]


def test_token_f1():
    assert token_f1("the cat sat", "the cat sat") == 1.0
    assert token_f1("the cat", "the dog") <= 0.5
    assert token_f1("", "anything") == 0.0


def test_groundedness():
    assert groundedness("hosted the backend on PythonAnywhere",
                        "He hosted the Python backend on PythonAnywhere.") == 1.0
    assert groundedness("trained a neural network on GPUs",
                        "The weather in Warsaw was cold.") < 0.4


def test_heuristic_judge_flags_hallucination():
    judge = HeuristicJudge(TfidfSimilarity().fit(["a", "b"]))
    grade = judge.grade({
        "question": "q",
        "context": "Omar hosted the backend on PythonAnywhere.",
        "reference": "He hosted the backend.",
        "prediction": "She trained convolutional networks on satellite imagery for land classification.",
    })
    assert grade["hallucination_flag"] is True
    assert grade["verdict"] == "fail"


def test_runner_aggregates_and_finds_the_hallucination():
    result = run_evaluation(BASE / "examples/qa_dataset.jsonl")
    agg = result["aggregates"]
    assert agg["items"] == 5
    assert 0 < agg["hallucination_rate"] < 1
    # item 2 is the planted hallucination
    assert result["rows"][1]["hallucination_flag"] is True
    assert result["rows"][0]["verdict"] == "pass"


if __name__ == "__main__":
    test_token_f1()
    test_groundedness()
    test_heuristic_judge_flags_hallucination()
    test_runner_aggregates_and_finds_the_hallucination()
    print("scorer tests passed")
