import re
from typing import Iterable, List

from .models import ClaimResult


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "in", "is", "it", "of", "on", "or", "that", "the", "this", "to",
    "was", "were", "with",
}


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {word for word in words if word not in STOPWORDS and len(word) > 1}


def extract_claims(answer: str) -> List[str]:
    """Split an answer into simple sentence-level claims for the MVP."""
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", answer.strip()) if part.strip()]


def verify_claim(claim: str, evidence: Iterable[str], threshold: float = 0.55) -> ClaimResult:
    claim_tokens = _tokens(claim)
    if not claim_tokens:
        return ClaimResult(claim=claim, support_score=0.0, supported=False)

    best = 0.0
    for passage in evidence:
        evidence_tokens = _tokens(passage)
        overlap = len(claim_tokens & evidence_tokens) / len(claim_tokens)
        best = max(best, overlap)

    return ClaimResult(claim=claim, support_score=round(best, 3), supported=best >= threshold)


def verify_answer(answer: str, evidence: Iterable[str]) -> List[ClaimResult]:
    passages = list(evidence)
    return [verify_claim(claim, passages) for claim in extract_claims(answer)]
