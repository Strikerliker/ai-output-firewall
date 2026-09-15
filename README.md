# AI Output Quality & Hallucination Firewall

An AWS-focused AI reliability project that evaluates LLM output against trusted evidence before allowing the answer to pass downstream.

## Goal

The firewall sits between a user and an LLM and produces a reliability decision:

`Question -> Amazon Bedrock -> LLM Answer -> Verification -> Score -> PASS / WARN / REJECT`

The current version uses the Amazon Bedrock Converse API for generation and a deterministic verification baseline. Later phases will add authoritative retrieval, AWS Lambda, API Gateway, DynamoDB, S3, and CloudWatch.

## MVP scoring

- **PASS**: score >= 80
- **WARN**: score >= 50 and < 80
- **REJECT**: score < 50

The verifier is intentionally deterministic and testable. Lexical overlap is a baseline, not proof of factual correctness; later retrieval and semantic verification will replace it.

## Amazon Bedrock setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure AWS credentials using the normal AWS SDK credential chain (for example, an AWS CLI profile or an IAM role). Never commit AWS access keys.

The runtime identity needs permission to invoke the selected Bedrock model, including `bedrock:InvokeModel`.

Optional environment variables:

```bash
export AWS_REGION=us-east-1
export BEDROCK_MODEL_ID=amazon.nova-micro-v1:0
```

`BEDROCK_MODEL_ID` can also be set to a supported Bedrock inference-profile ID or ARN.

Run the firewall:

```bash
python -m src.app
```

## Run tests

```bash
python -m pytest
```

The tests inject candidate answers directly, so the deterministic firewall tests do not require a live Bedrock call.

## Roadmap

1. Local deterministic verification baseline - complete
2. Amazon Bedrock generation - complete
3. Claim extraction and citation/evidence tracking
4. Authoritative-source retrieval / Bedrock Knowledge Bases
5. Lambda + API Gateway service
6. DynamoDB/S3 audit trail and CloudWatch metrics
7. Evaluation dataset and measured hallucination-detection performance
