import json
import logging
import os
import time
import uuid

import boto3

from src.app import run_firewall

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": os.getenv("ALLOWED_ORIGIN", "*")},
        "body": json.dumps(body),
    }


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
        body = json.loads(event.get("body") or "{}")
        question = str(body.get("question", "")).strip()
        supplied_answer = body.get("answer")
        if not question:
            return _response(400, {"error": "question is required"})

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
                {"claim": c.claim, "support_score": c.support_score, "supported": c.supported}
                for c in result.claims
            ],
            "evidence": [
                {"text": e.text, "source_uri": e.source_uri, "relevance_score": e.relevance_score}
                for e in evidence
            ],
            "latency_ms": round((time.time() - started) * 1000),
        }
        _audit({
            "request_id": request_id,
            "timestamp": int(time.time()),
            "decision": result.decision,
            "score": result.score,
            "question": question[:1000],
        })
        logger.info(json.dumps({"event": "firewall_evaluation", "request_id": request_id, "decision": result.decision, "score": result.score}))
        return _response(200, payload)
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        return _response(400, {"error": str(exc)})
    except Exception:
        logger.exception("Firewall request failed")
        return _response(500, {"error": "internal server error"})
