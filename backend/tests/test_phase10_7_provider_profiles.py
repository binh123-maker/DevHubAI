import os
import json
import pytest
from unittest.mock import patch, MagicMock
from app.services.ai.runtime import (
    Capability,
    ProviderProfile,
    ProviderRegistry,
    ProviderSelector,
    ProviderRuntime,
    ProviderResult,
    ProviderManifest
)
from app.services.ai.config import (
    ProviderConfigCenter,
    ProviderLoader,
    ProviderModel,
    ProviderCapabilityMatrix
)
from app.services.ai.health.monitor import HealthMonitor, ProviderHealthStatus
from app.services.ai.models.response import UnifiedResponse, UsageInfo

@pytest.fixture(autouse=True)
def reset_all_state():
    HealthMonitor.reset()
    ProviderRegistry.reset()
    ProviderCapabilityMatrix.reset()
    ProviderModel.reset()
    ProviderSelector.reset()
    yield
    HealthMonitor.reset()
    ProviderRegistry.reset()
    ProviderCapabilityMatrix.reset()
    ProviderModel.reset()
    ProviderSelector.reset()

def test_automatic_registration_on_startup():
    profiles = ProviderRegistry.get_all()
    assert len(profiles) >= 5
    provider_ids = [p.provider_id for p in profiles]
    assert "openai" in provider_ids
    assert "gemini" in provider_ids
    assert "groq" in provider_ids
    assert "ollama" in provider_ids
    assert "openrouter" in provider_ids

def test_provider_profile_fields():
    profile = ProviderRegistry.get("openai")
    assert profile is not None
    assert profile.provider_id == "openai"
    assert profile.display_name == "OpenAI"
    assert profile.enabled is True
    assert profile.priority == 10
    assert profile.api_key_name == "OPENAI_API_KEY"
    assert profile.api_key_env == "OPENAI_API_KEY"  # legacy alias
    assert profile.supports_chat is True
    assert profile.supports_reasoning is True
    assert profile.supports_rag is True
    assert profile.max_context_tokens == 128000
    assert profile.max_context == 128000  # legacy alias
    assert profile.timeout == 30.0
    assert profile.cooldown == 60.0
    assert profile.cooldown_seconds == 60.0  # legacy alias
    assert profile.cost_level == "high"
    assert profile.speed_level == "fast"
    assert profile.quality_level == "high"
    assert profile.health_status == "ONLINE"

def test_capability_discovery():
    reasoning_profiles = ProviderRegistry.profiles_for_capability(Capability.REASONING)
    r_ids = [p.provider_id for p in reasoning_profiles]
    assert "openai" in r_ids
    assert "groq" in r_ids
    assert "gemini" in r_ids

    embedding_profiles = ProviderRegistry.profiles_for_capability(Capability.EMBEDDING)
    e_ids = [p.provider_id for p in embedding_profiles]
    assert "ollama" in e_ids
    assert "openai" in e_ids

def test_priority_ordering():
    chain = ProviderSelector.select_candidate_chain(Capability.SUMMARIZATION)
    assert len(chain) > 0
    # First provider should be groq or gemini based on priority matrix
    assert chain[0]["provider"] in ("groq", "gemini", "openai")

def test_health_filtering():
    # Mark groq as UNAUTHORIZED
    HealthMonitor.record_failure("groq", error_type="AuthenticationError", status_code=401)
    groq_profile = ProviderRegistry.get("groq")
    assert groq_profile.health_status == "UNAUTHORIZED"

    # Selector must ignore groq automatically
    chain = ProviderSelector.select_candidate_chain(Capability.SUMMARIZATION)
    providers = [c["provider"] for c in chain]
    assert "groq" not in providers

def test_provider_enabling_and_disabling():
    ProviderConfigCenter.disable("openai")
    profile = ProviderConfigCenter.get_profile("openai")
    assert profile.enabled is False

    # Should not appear in candidate chain when disabled
    chain = ProviderSelector.select_candidate_chain(Capability.CHAT)
    providers = [c["provider"] for c in chain]
    assert "openai" not in providers

    # Re-enable
    ProviderConfigCenter.enable("openai")
    assert profile.enabled is True

def test_manifest_generation():
    manifest_data = ProviderManifest.get_manifest()
    assert manifest_data["version"] == "10.7.0"
    assert manifest_data["total_registered_providers"] >= 5

    json_manifest = ProviderManifest.generate_json()
    assert "OpenAI" in json_manifest

    md_manifest = ProviderManifest.generate_markdown()
    assert "# Provider Manifest" in md_manifest
    assert "| Provider | Display Name |" in md_manifest

    html_manifest = ProviderManifest.generate_html()
    assert "<html>" in html_manifest

def test_dynamic_reload():
    custom_dict = {
        "providers": {
            "custom_ai": {
                "display_name": "Custom AI Provider",
                "priority": 1,
                "capabilities": ["chat", "reasoning"],
                "default_model": "custom-model-v1"
            }
        }
    }
    ProviderLoader.load_from_dict(custom_dict)

    profile = ProviderRegistry.get("custom_ai")
    assert profile is not None
    assert profile.display_name == "Custom AI Provider"
    assert profile.priority == 1

@patch("app.services.ai.orchestrator.main.AIOrchestrator.generate_response")
def test_runtime_integration(mock_generate):
    mock_generate.return_value = UnifiedResponse(
        content="Profile Driven Response",
        provider="gemini",
        model="gemini-2.5-flash",
        usage=UsageInfo(input_tokens=10, output_tokens=20, total_tokens=30)
    )

    result = ProviderRuntime.execute(
        capability=Capability.DOCUMENT_QA,
        user_message="Test prompt"
    )

    assert isinstance(result, ProviderResult)
    assert result.provider_name == "gemini"
    assert result.response == "Profile Driven Response"
