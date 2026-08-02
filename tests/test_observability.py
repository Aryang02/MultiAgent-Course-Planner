from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.api.app import create_app
from src.observability.logging import configure_logging, get_logger
from src.observability.metrics import (
    record_llm_tokens,
    record_pipeline_duration,
    update_celery_queue_depth,
)
from src.serializers.backend import ReadyResponse


def test_configure_logging_json_mode():
    configure_logging(json_logs=True, log_level="INFO")
    logger = get_logger("test")
    assert logger is not None


def test_ready_response_includes_pinecone_field():
    response = ReadyResponse(
        status="ok",
        database="ok",
        redis="ok",
        pinecone="not_configured",
    )
    assert response.pinecone == "not_configured"


def test_health_endpoint_still_ok():
    client = TestClient(create_app(run_migrations_on_startup=False))
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_endpoint_reports_component_status():
    client = TestClient(create_app(run_migrations_on_startup=False))
    with patch("src.api.routes.health._check_database", return_value="ok"):
        with patch("src.api.routes.health._check_redis", return_value="ok"):
            with patch("src.api.routes.health._check_pinecone", return_value="not_configured"):
                response = client.get("/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert body["redis"] == "ok"
    assert body["pinecone"] == "not_configured"


def test_metrics_endpoint_exposed():
    client = TestClient(create_app(run_migrations_on_startup=False))
    with patch("src.observability.metrics.update_celery_queue_depth"):
        response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_request_duration" in response.text or "python_info" in response.text


def test_update_celery_queue_depth_reads_redis():
    mock_client = MagicMock()
    mock_client.llen.return_value = 3
    with patch("src.observability.metrics.redis.from_url", return_value=mock_client):
        update_celery_queue_depth()
    assert mock_client.llen.called


def test_record_pipeline_duration_and_llm_tokens():
    record_pipeline_duration(1.25)
    record_llm_tokens("gemini-1.5-pro", prompt_tokens=10, completion_tokens=20)


def test_llm_client_records_token_usage():
    from src.agents import llm_client

    response = MagicMock()
    response.text = "hello"
    response.usage_metadata = MagicMock(prompt_token_count=5, candidates_token_count=7)

    mock_model = MagicMock()
    mock_model.generate_content.return_value = response

    with patch.object(llm_client.genai, "configure"):
        with patch.object(llm_client.genai, "GenerativeModel", return_value=mock_model):
            with patch.object(llm_client.settings, "GOOGLE_API_KEY", "test-key"):
                with patch.object(llm_client, "record_llm_tokens") as mock_record:
                    result = llm_client.generate("system", "prompt")
    assert result == "hello"
    mock_record.assert_called_once_with("gemini-1.5-pro", 5, 7)
