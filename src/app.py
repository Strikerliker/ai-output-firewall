import os

from .generator import generate_answer
from .retriever import Evidence, retrieve_evidence
from .scorer import score_claims
from .verifier import verify_answer


DEMO_EVIDENCE = [
    Evidence(text="Amazon S3 supports server-side encryption for data at rest.", source_uri="demo://s3-encryption"),
    Evidence(text="Server-side encryption with AWS KMS keys is supported by Amazon S3.", source_uri="demo://s3-kms"),
]


def get_evidence(question: str) -> list[Evidence]:
    """Use Bedrock Knowledge Bases when configured; otherwise keep the local MVP runnable."""
    if os.environ.get("BEDROCK_KNOWLEDGE_BASE_ID"):
        return retrieve_evidence(question)
    return DEMO_EVIDENCE


def run_firewall(question: str, answer: str | None = None):
    candidate = answer if answer is not None else generate_answer(question)
    evidence = get_evidence(question)
    claims = verify_answer(candidate, [item.text for item in evidence])
    return candidate, score_claims(claims), evidence


def main() -> None:
    question = "What encryption does Amazon S3 support?"
    answer, result, evidence = run_firewall(question)

    print(f"Question: {question}")
    print(f"Answer: {answer}")
    print(f"Score: {result.score}/100")
    print(f"Decision: {result.decision}")
    print(f"Supported claims: {result.supported_claims}")
    print(f"Unsupported claims: {result.unsupported_claims}")
    print("Evidence:")
    for item in evidence:
        source = item.source_uri or "unknown source"
        relevance = f" relevance={item.relevance_score:.3f}" if item.relevance_score is not None else ""
        print(f"- {source}{relevance}: {item.text[:180]}")


if __name__ == "__main__":
    main()
