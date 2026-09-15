import base64
import json
import logging
import os
import time
import uuid

import boto3

from src.app import run_firewall

logger = logging.getLogger()
logger.setLevel(logging.INFO)

MAX_QUESTION_CHARS = 4_000
MAX_ANSWER_CHARS = 20_000


def _cors_headers():
    return {
        "Access-Control-Allow-Origin": os.getenv("ALLOWED_ORIGIN", "*"),
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST,OPTIONS",
    }


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json", **_cors_headers()},
        "body": json.dumps(body),
    }


def _request_body(event):
    raw_body = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        raw_body = base64.b64decode(raw_body, validate=True).decode("utf-8")

    body = json.loads(raw_body)
    if not isinstance(body, dict):
        raise ValueError("request body must be a JSON object")
    return body


def _validated_text(body, field, *, required, max_chars):
    value = body.get(field)
    if value is None:
        if required:
            raise ValueError(f"{field} is required")
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string")

    value = value.strip()
    if required and not value:
        raise ValueError(f"{field} is required")
    if len(value) > max_chars:
        raise ValueError(f"{field} must be {max_chars} characters or fewer")
    return value


def _audit(record):
    table_name = os.getenv("AUDIT_TABLE")
    if not table_name:
        return
    try:
        boto3.resource("dynamodb").Table(table_name).put_item(Item=record)
    except Exception:
        logger.exception("Audit write failed")


def lambda_handler(event, context):
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return _response(204, {})

    try:
        body = _request_body(event)
        question = _validated_text(
            body, "question", required=True, max_chars=MAX_QUESTION_CHARS
        )
        supplied_answer = _validated_text(
            body, "answer", required=False, max_chars=MAX_ANSWER_CHARS
        )

        started = time.time()
        answer, result, evidence = run_firewall(question, supplied_answer)
        request_id = getattr(context, "aws_request_id", None) or str(uuid.uuid4())
        payload = {
            "request_id": request_id,
            "question": question,
            "answer": answer,
            "score": result.score,
            "decision": result.decision,
            "supported_claims": result.supported_claims,
            "unsupported_claims": result.unsupported_claims,
            "claims": [
                {
                    "claim": claim.claim,
                    "support_score": claim.support_score,
                    "supported": claim.supported,
                }
                for claim in result.claims
            ],
            "evidence": [
                {
                    "text": item.text,
                    "source_uri": item.source_uri,
                    "relevance_score": item.relevance_score,
                }
                for item in evidence
            ],
            "latency_ms": round((time.time() - started) * 1000),
        }
        _audit(
            {
                "request_id": request_id,
                "timestamp": int(time.time()),
                "decision": result.decision,
                "score": result.score,
                "question": question[:1000],
            }
        )
        logger.info(
            json.dumps(
                {
                    "event": "firewall_evaluation",
                    "request_id": request_id,
                    "decision": result.decision,
                    "score": result.score,
                }
            )
        )
        return _response(200, payload)
    except (ValueError, TypeError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return _response(400, {"error": str(exc)})
    except Exception:
        logger.exception("Firewall request failed")
        return _response(500, {"error": "internal server error"})
