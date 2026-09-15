def generate_answer(question: str) -> str:
    """MVP placeholder. Amazon Bedrock generation will replace this in Phase 2."""
    demo_answers = {
        "What encryption does Amazon S3 support?": (
            "Amazon S3 supports server-side encryption. "
            "S3 can use AWS KMS keys for server-side encryption."
        )
    }
    return demo_answers.get(question, "No demo answer is configured for this question.")
