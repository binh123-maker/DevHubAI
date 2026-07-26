import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.ai.config.provider_env_loader import ProviderEnvLoader
from app.services.ai.config.provider_loader import ProviderLoader
from app.services.ai.config.provider_model import ProviderModel
from app.services.ai.config.provider_consistency_validator import ProviderConsistencyValidator
from app.services.ai.runtime.provider_registry import ProviderRegistry
from app.services.ai.runtime.provider_runtime import ProviderRuntime
from app.services.ai.runtime.provider_capability import Capability
from app.services.ai.runtime.runtime_trace import TraceStore
from app.services.ai.runtime.runtime_dashboard import RuntimeDashboard
from app.services.ai.runtime.provider_manifest import ProviderManifest

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    ProviderRegistry.reset()
    ProviderModel.reset()
    TraceStore.clear()
    ProviderLoader.load_and_register_all()
    yield
    ProviderRegistry.reset()
    ProviderModel.reset()
    TraceStore.clear()
    ProviderLoader.load_and_register_all()

def test_1_provider_env_loader_reads_models(monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-custom")
    monkeypatch.setenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
    monkeypatch.setenv("GROQ_MODEL", "mixtral-8x7b-32768")

    assert ProviderEnvLoader.get_model("openai") == "gpt-4o-custom"
    assert ProviderEnvLoader.get_model("openrouter") == "google/gemini-2.5-flash"
    assert ProviderEnvLoader.get_model("groq") == "mixtral-8x7b-32768"
    assert ProviderEnvLoader.get_model("nonexistent") is None

def test_2_provider_loader_overrides_defaults(monkeypatch):
    monkeypatch.setenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
    
    # Reload profiles
    ProviderRegistry.reset()
    loaded = ProviderLoader.load_and_register_all()
    
    openrouter_prof = ProviderRegistry.get("openrouter")
    assert openrouter_prof is not None
    assert openrouter_prof.default_model == "google/gemini-2.5-flash"
    assert openrouter_prof.supported_models[0] == "google/gemini-2.5-flash"

def test_3_provider_profile_reflects_env(monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    ProviderRegistry.reset()
    ProviderLoader.load_and_register_all()

    openai_prof = ProviderRegistry.get("openai")
    assert openai_prof.default_model == "gpt-4o-mini"
    resolved = ProviderModel.resolve_model("openai", "chat")
    assert resolved == "gpt-4o-mini"

def test_4_provider_runtime_executes_provider_profile_model(monkeypatch):
    monkeypatch.setenv("OPENROUTER_MODEL", "deepseek/deepseek-chat-v3:free")
    ProviderRegistry.reset()
    ProviderLoader.load_and_register_all()

    res_details = ProviderModel.get_resolution_details("openrouter", "chat")
    assert res_details["resolved_model"] == "deepseek/deepseek-chat-v3:free"
    assert res_details["model_source"] == "ENV"
    assert res_details["override_applied"] is True

def test_5_dashboard_returns_provider_profile_model(monkeypatch):
    monkeypatch.setenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
    ProviderRegistry.reset()
    ProviderLoader.load_and_register_all()

    snapshot = RuntimeDashboard.get_snapshot()
    openrouter_entry = next((p for p in snapshot["providers"] if p["provider_id"] == "openrouter"), None)
    assert openrouter_entry is not None
    assert openrouter_entry["current_model"] == "google/gemini-2.5-flash"

    manifest = ProviderManifest.get_manifest()
    manifest_entry = next((p for p in manifest["providers"] if p["provider_id"] == "openrouter"), None)
    assert manifest_entry is not None
    assert manifest_entry["default_model"] == "google/gemini-2.5-flash"

def test_6_runtime_trace_stores_resolved_model(monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    ProviderRegistry.reset()
    ProviderLoader.load_and_register_all()

    with patch("app.services.ai.orchestrator.main.AIOrchestrator.generate_response") as mock_gen:
        from app.services.ai.models.response import UnifiedResponse, UsageInfo
        mock_gen.return_value = UnifiedResponse(
            content="Hello test",
            provider="openai",
            model="gpt-4o-mini",
            usage=UsageInfo(input_tokens=10, output_tokens=10, total_tokens=20)
        )
        result = ProviderRuntime.execute(Capability.CHAT, "Hello")
        assert result.success is True

        traces = TraceStore.get_recent_traces(limit=1)
        assert len(traces) > 0
        latest = traces[0]
        assert latest["selected_model"] == "gpt-4o-mini"
        assert latest["model_source"] == "ENV"

def test_7_runtime_config_endpoint(monkeypatch):
    monkeypatch.setenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
    ProviderRegistry.reset()
    ProviderLoader.load_and_register_all()

    res = client.get("/api/v1/system/runtime/config")
    assert res.status_code == 200
    configs = res.json()
    assert isinstance(configs, list)
    openrouter_cfg = next((c for c in configs if c["provider"] == "openrouter"), None)
    assert openrouter_cfg is not None
    assert openrouter_cfg["model"] == "google/gemini-2.5-flash"
    assert openrouter_cfg["source"] == "ProviderProfile"

def test_8_provider_consistency_validator(monkeypatch):
    monkeypatch.setenv("GROQ_MODEL", "mixtral-8x7b-32768")
    ProviderRegistry.reset()
    ProviderLoader.load_and_register_all()

    report = ProviderConsistencyValidator.validate_consistency()
    assert report.overall_status == "PASS"
    assert report.total_providers > 0
    assert report.failed_providers == 0

    groq_detail = next((d for d in report.details if d.provider == "groq"), None)
    assert groq_detail is not None
    assert groq_detail.expected_model == "mixtral-8x7b-32768"
    assert groq_detail.runtime_model == "mixtral-8x7b-32768"
    assert groq_detail.dashboard_model == "mixtral-8x7b-32768"
    assert groq_detail.plugin_model == "mixtral-8x7b-32768"
    assert groq_detail.status == "PASS"

def test_9_no_runtime_dependency_on_default_provider_models():
    # Verify ProviderModel.resolve_model works cleanly without DEFAULT_PROVIDER_MODELS dict
    from app.services.ai.config.provider_model import ProviderModel
    res = ProviderModel.resolve_model("openai", "chat")
    assert res is not None
    assert isinstance(res, str)
