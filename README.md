# AI Output Quality & Hallucination Firewall

An AWS-focused AI reliability project that evaluates LLM output against trusted evidence before allowing the answer to pass downstream.

![AI Output Firewall AWS Architecture](docs/architecture.svg)

## Why this project exists

LLMs can produce fluent answers that are incomplete, weakly sourced, or false. This project separates **generation** from **verification** and treats model output as untrusted until claims are checked against a controlled evidence boundary.

`Question -> Amazon Bedrock -> Candidate Answer -> Trusted Retrieval -> Claim Verification -> Score -> PASS / WARN / REJECT`

## Portfolio capabilities

- Amazon Bedrock Converse API generation
- Bedrock Knowledge Bases retrieval with source provenance
- Sentence-level claim extraction and deterministic support scoring
- PASS / WARN / REJECT enforcement policy
- Interactive Streamlit reviewer dashboard
- Serverless Lambda + API Gateway-compatible HTTP API
- DynamoDB audit records and structured CloudWatch logs
- AWS SAM infrastructure-as-code
- Offline regression/evaluation dataset
- Pytest suite and GitHub Actions CI
- Local fallback evidence so reviewers can run the verification path without AWS credentials

## Decision policy

| Decision | Score | Meaning |
|---|---:|---|
| PASS | 80-100 | Evidence sufficiently supports the candidate response |
| WARN | 50-79 | Mixed or incomplete support; human review recommended |
| REJECT | 0-49 | Evidence does not sufficiently support the response |

The current lexical verifier is intentionally transparent and deterministic. It is a baseline, not a claim that hallucination detection is solved. A production extension would add semantic entailment/LLM-as-judge verification and benchmark it against labeled data.

## Run the dashboard

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run dashboard.py
```

## Run tests

```bash
python -m pytest -q
```

## AWS configuration

Use the standard AWS SDK credential chain. Never commit access keys.

```bash
export AWS_REGION=us-east-1
export BEDROCK_MODEL_ID=amazon.nova-micro-v1:0
export BEDROCK_KNOWLEDGE_BASE_ID=YOUR_KNOWLEDGE_BASE_ID
```

For a portfolio deployment, populate the Knowledge Base with curated authoritative material stored in S3 and retain provenance metadata.

## Deploy the API with AWS SAM

```bash
sam build
sam deploy --guided
```

`template.yaml` creates the Lambda-backed HTTP endpoint and a DynamoDB audit table. The function returns the answer, score, decision, claim-level results, evidence provenance, and latency.

## Security and reliability choices

- No AWS credentials are stored in source code.
- Generation and verification are separate trust stages.
- Knowledge Base sources are surfaced for auditability.
- Audit writes are deliberately non-blocking.
- API errors avoid returning internal exception details.
- CI executes the offline test suite on pushes and pull requests.
- The trusted corpus is an explicit security boundary.

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for the full graphical architecture and explanation.

## Interview talking points

This project demonstrates practical GenAI engineering beyond prompt design: RAG, evidence provenance, deterministic policy enforcement, serverless APIs, IAM-aware AWS architecture, observability, infrastructure-as-code, testing, and measurable evaluation. The central design decision is that a model is **not allowed to verify itself using fluency as evidence**.

## Next production extensions

Semantic entailment scoring, a larger labeled benchmark, CloudWatch custom metrics/alarms, authentication/rate limiting, and a production Knowledge Base remain appropriate next-stage improvements. They are intentionally identified rather than represented as already deployed.
