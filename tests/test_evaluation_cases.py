import json
from pathlib import Path

from src.app import run_firewall


def test_evaluation_cases_match_expected_decisions():
    cases = json.loads(Path("data/evaluation.json").read_text())
    for case in cases:
        _, result, _ = run_firewall(case["question"], case["answer"])
        assert result.decision == case["expected_decision"], case["id"]
