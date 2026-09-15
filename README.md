# AI Output Quality & Hallucination Firewall

An AWS-focused AI reliability project that evaluates LLM output against trusted evidence before allowing the answer to pass downstream.

## Goal

`Question -> Amazon Bedrock -> LLM Answer -> Knowledge Base Retrieval -> Claim Verification -> Score -> PASS / WARN / REJECT`

The project separates generation from verification: a fluent model response is never treated as evidence of correctness.

## Current capabilities

- Interactive Streamlit dashboard
- Amazon Bedrock Converse API generation
- Bedrock Knowledge Bases retrieval through `bedrock-agent-runtime`
- Evidence objects with source URI and retrieval relevance score
- Sentence-level claim extraction
- Deterministic support scoring
- PASS / WARN / REJECT policy
- Offline tests that do not require AWS calls

## Dashboard

The dashboard lets a reviewer either generate an answer with Amazon Bedrock or paste a candidate LLM answer for verification. It displays the overall quality score, PASS/WARN/REJECT decision, supported and unsupported claim counts, per-claim support scores, and retrieved evidence with provenance.

Install dependencies and launch it locally:

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

Supplied-answer mode can be used without a live Bedrock generation call. Live generation requires valid AWS credentials and Bedrock model access.

## Scoring

- **PASS**: score >= 80
- **WARN**: score >= 50 and < 80
- **REJECT**: score < 50

Lexical overlap is deliberately only a baseline. A later phase will add semantic/LLM-based claim verification and measured evaluation metrics.

## AWS setup

Configure AWS credentials using the standard AWS SDK credential chain (AWS CLI profile, IAM role, etc.). Never commit AWS access keys.

Set configuration:

```bash
export AWS_REGION=us-east-1
export BEDROCK_MODEL_ID=amazon.nova-micro-v1:0
export BEDROCK_KNOWLEDGE_BASE_ID=YOUR_KNOWLEDGE_BASE_ID
```

The runtime identity needs permission for the Bedrock model invocation and Knowledge Base retrieval actions it uses.

When `BEDROCK_KNOWLEDGE_BASE_ID` is configured, the firewall retrieves evidence from that Knowledge Base. Without it, the repository keeps a small local evidence set so the verification MVP remains runnable and testable.

## Knowledge Base data

For the portfolio deployment, use an Amazon S3-backed Bedrock Knowledge Base containing curated authoritative material. Keep provenance/metadata with the source documents so retrieved evidence can be audited.

Do not scrape arbitrary internet content into the trusted corpus. The point of the firewall is to verify against an explicitly controlled evidence boundary.

## CLI

```bash
python -m src.app
```

## Test

```bash
python -m pytest
```

## Roadmap

1. Local deterministic verification baseline - complete
2. Amazon Bedrock generation - complete
3. Evidence objects and source tracking - complete
4. Bedrock Knowledge Base retrieval - code complete; AWS resource configuration required
5. Interactive dashboard - complete
6. Semantic claim verification
7. Lambda + API Gateway service
8. DynamoDB/S3 audit trail and CloudWatch metrics
9. Evaluation harness and measured hallucination-detection performance
