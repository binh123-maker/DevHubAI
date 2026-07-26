import pytest
from unittest.mock import patch
from app.services.ai.runtime import (
    Capability,
    ProviderProfile,
    ProviderRegistry,
    ProviderAlias,
    ProviderSelector,
    ProviderRuntime,
    ProviderStatistics,
    ProviderManifest
)
from app.services.ai.config import (
    ProviderConfigCenter,
    ProviderLoader,
    ProviderModel,
    ProviderCapabilityMatrix
)
from app.services.ai.health.monitor import HealthMonitor, ProviderHealthStatus

@pytest.fixture(autouse=True)
def reset_intelligence_state():
    HealthMonitor.reset()
    ProviderRegistry.reset()
    ProviderCapabilityMatrix.reset()
    ProviderModel.reset()
    ProviderAlias.reset()
    ProviderSelector.reset()
    ProviderStatistics.reset()
    yield
    HealthMonitor.reset()
    ProviderRegistry.reset()
    ProviderCapabilityMatrix.reset()
    ProviderModel.reset()
    ProviderAlias.reset()
    ProviderSelector.reset()
    ProviderStatistics.reset()

def test_provider_alias_layer():
    assert ProviderConfigCenter.resolve_alias("chat-ai") == "groq"
    assert ProviderConfigCenter.resolve_alias("summary-ai") == "gemini"
    assert ProviderConfigCenter.resolve_alias("embedding-ai") == "ollama"

    # Register custom alias
    ProviderConfigCenter.register_alias("fast-code-ai", "groq")
    assert ProviderConfigCenter.resolve_alias("fast-code-ai") == "groq"

    # Update alias dynamically
    ProviderConfigCenter.register_alias("chat-ai", "openai")
    assert ProviderConfigCenter.resolve_alias("chat-ai") == "openai"

def test_provider_groups_and_routing():
    openai_p = ProviderRegistry.get("openai")
    ollama_p = ProviderRegistry.get("ollama")
    assert openai_p.group == "cloud"
    assert ollama_p.group == "local"

    # CLOUD_ONLY policy
    ProviderConfigCenter.set_group_policy("CLOUD_ONLY")
    chain = ProviderSelector.select_candidate_chain("chat")
    providers = [c["provider"] for c in chain]
    assert "ollama" not in providers
    assert "openai" in providers

    # LOCAL_ONLY policy
    ProviderConfigCenter.set_group_policy("LOCAL_ONLY")
    chain_local = ProviderSelector.select_candidate_chain("chat")
    providers_local = [c["provider"] for c in chain_local]
    assert "openai" not in providers_local
    assert "ollama" in providers_local

def test_runtime_statistics_updates():
    ProviderStatistics.record_execution(
        provider_name="groq",
        success=True,
        latency_ms=120.0,
        prompt_tokens=100,
        completion_tokens=50,
        is_fallback=False
    )

    stats = ProviderStatistics.get_stats("groq")
    assert stats["total_requests"] == 1
    assert stats["successful_requests"] == 1
    assert stats["average_latency"] == 120.0
    assert stats["total_prompt_tokens"] == 100
    assert stats["total_completion_tokens"] == 50
    assert stats["uptime"] == 100.0

    # Profile statistics synced
    profile = ProviderRegistry.get("groq")
    assert profile.statistics["total_requests"] == 1
    assert profile.health_score == 1.0

def test_provider_benchmark_scoring_and_policies():
    profile = ProviderRegistry.get("groq")
    score_balanced = profile.calculate_score("BALANCED")
    score_health = profile.calculate_score("BEST_HEALTH")
    assert score_balanced > 0.0
    assert score_health == 100.0

    # Switch policy mode to LOWEST_LATENCY
    ProviderConfigCenter.set_policy("LOWEST_LATENCY")
    assert ProviderConfigCenter.get_policy() == "LOWEST_LATENCY"

    chain = ProviderSelector.select_candidate_chain("chat")
    assert len(chain) > 0

def test_dynamic_enable_disable_pause_resume():
    # Pause provider
    ProviderConfigCenter.pause("groq", duration_seconds=60.0)
    groq_p = ProviderRegistry.get("groq")
    assert groq_p.health_status == "PAUSED"
    assert HealthMonitor.is_provider_healthy("groq") is False

    # Selector skips paused provider
    chain = ProviderSelector.select_candidate_chain("chat")
    providers = [c["provider"] for c in chain]
    assert "groq" not in providers

    # Resume provider
    ProviderConfigCenter.resume("groq")
    assert groq_p.health_status == "HEALTHY"
    assert HealthMonitor.is_provider_healthy("groq") is True

def test_future_provider_ready():
    # Simulate adding Claude (Anthropic) provider with zero runtime changes
    claude_profile_data = {
        "provider_id": "claude",
        "display_name": "Anthropic Claude",
        "description": "State-of-the-art Claude 3.5 Sonnet model",
        "priority": 5,
        "enabled": True,
        "default_model": "claude-3-5-sonnet",
        "supported_models": ["claude-3-5-sonnet", "claude-3-haiku"],
        "capabilities": ["chat", "reasoning", "code_generation"],
        "supports_chat": True,
        "supports_reasoning": True,
        "group": "cloud"
    }

    profile = ProviderLoader.create_profile("claude", claude_profile_data)
    ProviderRegistry.register(profile)

    fetched = ProviderRegistry.get("claude")
    assert fetched is not None
    assert fetched.display_name == "Anthropic Claude"
    assert fetched.supports_capability("reasoning") is True

    # Candidate chain includes new provider dynamically
    chain = ProviderSelector.select_candidate_chain("reasoning")
    providers = [c["provider"] for c in chain]
    assert "claude" in providers

def test_extended_metadata_and_manifest():
    manifest = ProviderManifest.get_manifest()
    assert "active_policy" in manifest
    assert "active_group_policy" in manifest
    assert "aliases" in manifest
    assert "providers" in manifest

    json_str = ProviderManifest.generate_json()
    assert "active_policy" in json_str

    md_str = ProviderManifest.generate_markdown()
    assert "# Provider Manifest" in md_str
    assert "Registered Aliases" in md_str

def test_dynamic_reload():
    ProviderConfigCenter.set_policy("BEST_HEALTH")
    ProviderConfigCenter.register_alias("custom-alias", "openai")

    ProviderConfigCenter.reload()
    assert len(ProviderRegistry.get_all()) >= 5
    assert ProviderConfigCenter.resolve_alias("custom-alias") == "openai"
