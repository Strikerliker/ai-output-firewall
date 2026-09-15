# Architecture Diagram

The diagram below shows the portfolio reference architecture for the AI Output Quality & Hallucination Firewall.

![AI Output Firewall AWS Architecture](architecture.svg)

The architecture separates candidate generation from evidence verification. API Gateway fronts a Lambda workflow; Amazon Bedrock generates candidate responses, curated S3 content and a Bedrock Knowledge Base provide the trusted evidence boundary, DynamoDB records audit decisions, and CloudWatch provides operational telemetry. The verifier returns PASS, WARN, or REJECT with evidence provenance.
