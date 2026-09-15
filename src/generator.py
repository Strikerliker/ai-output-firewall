import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError


DEFAULT_MODEL_ID = "amazon.nova-micro-v1:0"
SYSTEM_PROMPT = (
    "You are the generation component of an AI reliability test system. "
    "Answer the user's question concisely and factually. Do not invent facts."
)


def generate_answer(question: str) -> str:
    """Generate an answer with Amazon Bedrock's Converse API.

    BEDROCK_MODEL_ID can be a supported foundation-model ID or inference-profile
    ID/ARN. AWS_REGION controls the Bedrock Runtime region.
    """
    model_id = os.getenv("BEDROCK_MODEL_ID", DEFAULT_MODEL_ID)
    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    client = boto3.client("bedrock-runtime", region_name=region)

    try:
        response = client.converse(
            modelId=model_id,
            system=[{"text": SYSTEM_PROMPT}],
            messages=[
                {
                    "role": "user",
                    "content": [{"text": question}],
                }
            ],
            inferenceConfig={
                "maxTokens": 512,
                "temperature": 0.1,
                "topP": 0.9,
            },
        )
    except (ClientError, BotoCoreError) as exc:
        raise RuntimeError(f"Amazon Bedrock generation failed: {exc}") from exc

    content = response.get("output", {}).get("message", {}).get("content", [])
    text_parts = [item["text"] for item in content if "text" in item]
    if not text_parts:
        raise RuntimeError("Amazon Bedrock returned no text content.")

    return "\n".join(text_parts).strip()
