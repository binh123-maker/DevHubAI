import pytest
from app.services.ai.policy import PolicyEngine, PolicyLoader, PolicyProfile
from app.services.ai.config.provider_capability_matrix import ProviderCapabilityMatrix

@pytest.fixture(autouse=True)
def reset_policy_state():
    PolicyEngine.reset()
    yield
    PolicyEngine.reset()

def test_policy_loader():
    policies = PolicyLoader.list_available_policies()
    assert "production" in policies
    assert "development" in policies
    assert "cheap" in policies
    assert "reasoning" in policies
    assert "coding" in policies

    prod_profile = PolicyLoader.load_policy("production")
    assert prod_profile is not None
    assert prod_profile.name == "production"
    assert "chat" in prod_profile.priorities

def test_policy_engine_switching():
    assert PolicyEngine.get_policy() == "production"

    # Switch to development
    success = PolicyEngine.set_policy("development")
    assert success is True
    assert PolicyEngine.get_policy() == "development"

    chain = ProviderCapabilityMatrix.get_priority_chain("chat")
    assert chain[0] == "ollama"

    # Switch to cheap
    PolicyEngine.set_policy("cheap")
    assert PolicyEngine.get_policy() == "cheap"
    chain_cheap = ProviderCapabilityMatrix.get_priority_chain("chat")
    assert chain_cheap[0] == "groq"
