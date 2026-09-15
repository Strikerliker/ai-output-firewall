from dataclasses import dataclass, field
from typing import List


@dataclass
class ClaimResult:
    claim: str
    support_score: float
    supported: bool


@dataclass
class FirewallResult:
    score: int
    decision: str
    supported_claims: int
    unsupported_claims: int
    claims: List[ClaimResult] = field(default_factory=list)
