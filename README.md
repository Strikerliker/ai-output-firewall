# AI Output Quality & Hallucination Firewall

An AWS-focused AI reliability project that evaluates LLM output against trusted evidence before allowing the answer to pass downstream.

## Goal

The firewall sits between a user and an LLM and produces a reliability decision:

`Question -> LLM Answer -> Verification -> Score -> PASS / WARN / REJECT`

The MVP measures claim support against authoritative context. Later phases will add Amazon Bedrock, retrieval, AWS Lambda, API Gateway, DynamoDB, S3, and CloudWatch.

## MVP scoring

- **PASS**: score >= 80
- **WARN**: score >= 50 and < 80
- **REJECT**: score < 50

The first implementation is intentionally deterministic and testable. It does not pretend that lexical overlap alone proves factual correctness; it provides a baseline that later semantic and retrieval-based verification can replace.

## Run locally

```bash
python -m src.app
```

## Run tests

```bash
python -m pytest
```

## Roadmap

1. Local deterministic verification baseline
2. Claim extraction and citation/evidence tracking
3. Amazon Bedrock integration
4. Authoritative-source retrieval / Bedrock Knowledge Bases
5. Lambda + API Gateway service
6. DynamoDB/S3 audit trail and CloudWatch metrics
7. Evaluation dataset and measured hallucination-detection performance
