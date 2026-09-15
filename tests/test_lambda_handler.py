import json
from types import SimpleNamespace

import lambda_handler


def _event(body, method="POST"):
    return {
        "requestContext": {"http": {"method": method}},
        "body": json.dumps(body),
    }


def test_evaluate_returns_result_and_cors_headers(monkeypatch):
    monkeypatch.delenv("AUDIT_TABLE", raising=False)
    monkeypatch.setenv("ALLOWED_ORIGIN", "https://example.com")

    response = lambda_handler.lambda_handler(
        _event(
            {
                "question": "What encryption does Amazon S3 support?",
                "answer": "Amazon S3 supports server-side encryption for data at rest.",
            }
        ),
        SimpleNamespace(aws_request_id="request-123"),
    )

    payload = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert payload["request_id"] == "request-123"
    assert payload["decision"] == "PASS"
    assert response["headers"]["Access-Control-Allow-Origin"] == "https://example.com"
    assert response["headers"]["Access-Control-Allow-Methods"] == "POST,OPTIONS"


def test_options_returns_cors_preflight_response():
    response = lambda_handler.lambda_handler(
        _event({}, method="OPTIONS"), SimpleNamespace(aws_request_id="request-123")
    )

    assert response["statusCode"] == 204
    assert response["headers"]["Access-Control-Allow-Headers"] == "Content-Type"


def test_rejects_invalid_or_oversized_inputs():
    invalid_cases = [
        [],
        {"question": 123},
        {"question": "x" * (lambda_handler.MAX_QUESTION_CHARS + 1)},
        {"question": "valid", "answer": 123},
        {
            "question": "valid",
            "answer": "x" * (lambda_handler.MAX_ANSWER_CHARS + 1),
        },
    ]

    for body in invalid_cases:
        response = lambda_handler.lambda_handler(
            _event(body), SimpleNamespace(aws_request_id="request-123")
        )
        assert response["statusCode"] == 400
