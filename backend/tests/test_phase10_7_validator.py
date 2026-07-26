import pytest
from app.services.ai.config.configuration_validator import ConfigurationValidator

def test_configuration_validator():
    report = ConfigurationValidator.validate_all()
    assert "system_valid" in report
    assert "total_providers_scanned" in report
    assert "available_policies" in report
    assert "active_policy" in report
    assert report["total_providers_scanned"] >= 5
