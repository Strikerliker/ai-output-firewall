from src.app import run_firewall
from src.scorer import decision_for_score


def test_decision_thresholds():
    assert decision_for_score(80) == "PASS"
    assert decision_for_score(79) == "WARN"
    assert decision_for_score(50) == "WARN"
    assert decision_for_score(49) == "REJECT"


def test_supported_s3_answer_passes(monkeypatch):
    monkeypatch.delenv("BEDROCK_KNOWLEDGE_BASE_ID", raising=False)
    answer = "Amazon S3 supports server-side encryption. S3 can use AWS KMS keys for server-side encryption."
    _, result, evidence = run_firewall("What encryption does Amazon S3 support?", answer)
    assert result.decision == "PASS"
    assert result.unsupported_claims == 0
    assert evidence


def test_obvious_hallucination_is_rejected(monkeypatch):
    monkeypatch.delenv("BEDROCK_KNOWLEDGE_BASE_ID", raising=False)
    answer = "Amazon S3 requires a fictional QuantumShield encryption algorithm for every object."
    _, result, evidence = run_firewall("What encryption does Amazon S3 support?", answer)
    assert result.decision == "REJECT"
    assert result.unsupported_claims == 1
    assert evidence
