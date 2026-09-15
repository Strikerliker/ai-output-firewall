# Architecture

## MVP

```text
User Question
     |
     v
LLM / Generator
     |
     v
Claim Extraction
     |
     v
Evidence Verification
     |
     v
Quality Scoring
     |
     +---- PASS
     +---- WARN
     +---- REJECT
```

## Target AWS architecture

The production-oriented version will evolve toward:

```text
Client
  -> Amazon API Gateway
  -> AWS Lambda (firewall orchestrator)
       -> Amazon Bedrock (generation)
       -> Authoritative retrieval / Bedrock Knowledge Bases
       -> Verification + scoring policy
       -> DynamoDB / S3 audit record
       -> CloudWatch metrics and logs
  -> PASS / WARN / REJECT response
```

## Design principle

Generation and verification should be separable. A fluent model response is not treated as evidence of correctness. The verifier evaluates claims against retrieved trusted evidence and exposes the decision and supporting metrics for auditing.
