from typing import List

from .models import ClaimResult, FirewallResult


def decision_for_score(score: int) -> str:
    if score >= 80:
        return "PASS"
    if score >= 50:
        return "WARN"
    return "REJECT"


def score_claims(claims: List[ClaimResult]) -> FirewallResult:
    if not claims:
        return FirewallResult(0, "REJECT", 0, 0, [])

    average_support = sum(claim.support_score for claim in claims) / len(claims)
    score = round(average_support * 100)
    supported = sum(claim.supported for claim in claims)
    unsupported = len(claims) - supported

    return FirewallResult(
        score=score,
        decision=decision_for_score(score),
        supported_claims=supported,
        unsupported_claims=unsupported,
        claims=claims,
    )
