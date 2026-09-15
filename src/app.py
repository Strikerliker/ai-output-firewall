from .generator import generate_answer
from .scorer import score_claims
from .verifier import verify_answer


EVIDENCE = [
    "Amazon S3 supports server-side encryption for data at rest.",
    "Server-side encryption with AWS KMS keys is supported by Amazon S3.",
]


def run_firewall(question: str, answer: str | None = None):
    candidate = answer if answer is not None else generate_answer(question)
    claims = verify_answer(candidate, EVIDENCE)
    return candidate, score_claims(claims)


def main() -> None:
    question = "What encryption does Amazon S3 support?"
    answer, result = run_firewall(question)

    print(f"Question: {question}")
    print(f"Answer: {answer}")
    print(f"Score: {result.score}/100")
    print(f"Decision: {result.decision}")
    print(f"Supported claims: {result.supported_claims}")
    print(f"Unsupported claims: {result.unsupported_claims}")


if __name__ == "__main__":
    main()
