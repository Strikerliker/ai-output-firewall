import os
from dataclasses import dataclass
from typing import List, Optional

import boto3


@dataclass
class Evidence:
    text: str
    source_uri: Optional[str] = None
    relevance_score: Optional[float] = None


def retrieve_evidence(question: str, number_of_results: int = 5) -> List[Evidence]:
    """Retrieve trusted evidence from an Amazon Bedrock Knowledge Base."""
    knowledge_base_id = os.environ.get("BEDROCK_KNOWLEDGE_BASE_ID")
    if not knowledge_base_id:
        raise RuntimeError(
            "BEDROCK_KNOWLEDGE_BASE_ID is not set. Configure a Bedrock Knowledge Base before retrieval."
        )

    region = os.environ.get("AWS_REGION", "us-east-1")
    client = boto3.client("bedrock-agent-runtime", region_name=region)
    response = client.retrieve(
        knowledgeBaseId=knowledge_base_id,
        retrievalQuery={"text": question},
        retrievalConfiguration={
            "vectorSearchConfiguration": {"numberOfResults": number_of_results}
        },
    )

    evidence: List[Evidence] = []
    for item in response.get("retrievalResults", []):
        content = item.get("content", {})
        text = content.get("text")
        if not text:
            continue

        location = item.get("location", {})
        source_uri = None
        if "s3Location" in location:
            source_uri = location["s3Location"].get("uri")
        elif "webLocation" in location:
            source_uri = location["webLocation"].get("url")

        evidence.append(
            Evidence(
                text=text,
                source_uri=source_uri,
                relevance_score=item.get("score"),
            )
        )

    return evidence
