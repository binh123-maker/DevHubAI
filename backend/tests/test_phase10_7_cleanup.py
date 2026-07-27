import os
import pytest
from unittest.mock import patch, MagicMock
from app.services.ai.config import (
    ProviderConfigCenter,
    ProviderEnvLoader,
    ProviderModel,
    ProviderCapabilityMatrix,
    ProviderLoader,
    ProviderValidator,
    ProviderDeadCodeScanner
)
from app.services.ai.health.monitor import HealthMonitor, ProviderHealthStatus
from app.services.ai.runtime import (
    Capability,
    ProviderSelector,
    ProviderRuntime,
    ProviderResult,
    ProviderManifest
)
from app.services.ai.models.response import UnifiedResponse

@pytest.fixture(autouse=True)
def reset_config_state():
    ProviderModel.reset()
    ProviderCapabilityMatrix.reset()
    HealthMonitor.reset()
    yield
    ProviderModel.reset()
    ProviderCapabilityMatrix.reset()
    HealthMonitor.reset()

def test_provider_env_loader():
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-sk-key", "GROQ_API_KEY": "test-groq-key"}):
        assert ProviderEnvLoader.get_api_key("openai") == "test-sk-key"
        assert ProviderEnvLoader.get_api_key("groq") == "test-groq-key"

def test_dynamic_model_resolution():
    # Resolve default
    m1 = ProviderConfigCenter.resolve_model("openai", "chat")
    assert m1 == "gpt-4o"

    # Set custom override
    ProviderModel.set_custom_mapping("openai", "chat", "gpt-4o-custom")
    m2 = ProviderConfigCenter.resolve_model("openai", "chat")
    assert m2 == "gpt-4o-custom"

def test_provider_loader_custom_config():
    custom_dict = {
        "priorities": {
            "chat": ["groq", "gemini", "openai"]
        },
        "models": {
            "groq": {
                "chat": "llama-3.3-70b-custom"
            }
        }
    }

    ProviderLoader.load_config_dict(custom_dict)

    chain = ProviderCapabilityMatrix.get_priority_chain("chat")
    assert chain == ["groq", "gemini", "openai"]

    model = ProviderConfigCenter.resolve_model("groq", "chat")
    assert model == "llama-3.3-70b-custom"

def test_extended_health_monitor_cooldowns():
    # 429 Rate limit test
    HealthMonitor.record_failure("groq", error_type="RateLimitError", status_code=429, cooldown_seconds=180.0)
    assert HealthMonitor.is_provider_healthy("groq") is False
    snap = HealthMonitor.get_health_snapshot()["groq"]
    assert snap["status"] == ProviderHealthStatus.COOLDOWN
    assert snap["count_429"] == 1

    # 401 Unauthorized test
    HealthMonitor.record_failure("openai", error_type="AuthenticationError", status_code=401)
    assert HealthMonitor.is_provider_healthy("openai") is False
    snap_ai = HealthMonitor.get_health_snapshot()["openai"]
    assert snap_ai["status"] == ProviderHealthStatus.UNAUTHORIZED

def test_provider_validator():
    val = ProviderValidator.validate_all_providers()
    assert "system_valid" in val
    assert "providers" in val

def test_provider_manifest_formats():
    json_manifest = ProviderManifest.generate_json()
    assert "10.7.0" in json_manifest

    md_manifest = ProviderManifest.generate_markdown()
    assert "# Provider Manifest" in md_manifest
    assert "Display Name" in md_manifest

    html_manifest = ProviderManifest.generate_html()
    assert "<html>" in html_manifest
    assert "<h1>Provider Manifest" in html_manifest

def test_dead_code_scanner():
    scan_path = "app/services/ai" if os.path.exists("app/services/ai") else "backend/app/services/ai"
    res = ProviderDeadCodeScanner.scan_directory(scan_path)
    assert "scanned_files" in res
    assert res["scanned_files"] > 0

@patch("app.services.ai.orchestrator.main.AIOrchestrator.generate_response")
def test_automatic_provider_switching_runtime(mock_generate):
    mock_generate.return_value = UnifiedResponse(
        content="Success from Fallback Provider",
        provider="gemini",
        model="gemini-2.5-flash"
    )

    res = ProviderRuntime.execute(
        capability=Capability.DOCUMENT_QA,
        user_message="Summarize this document"
    )

    assert res.provider_name == "gemini"
    assert res.response == "Success from Fallback Provider"
