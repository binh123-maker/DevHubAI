import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from app.services.ai.runtime.provider_registry import ProviderRegistry
from app.services.ai.config.provider_model import ProviderModel
from app.services.ai.runtime.runtime_dashboard import RuntimeDashboard
from app.services.ai.config.provider_config import ProviderConfigCenter

logger = logging.getLogger(__name__)

class ProviderConsistencyItem(BaseModel):
    provider: str
    expected_model: str
    runtime_model: str
    dashboard_model: str
    plugin_model: str
    status: str  # PASS / FAIL

class ProviderConsistencyReport(BaseModel):
    overall_status: str  # PASS / FAIL
    total_providers: int
    passed_providers: int
    failed_providers: int
    details: List[ProviderConsistencyItem]

class ProviderConsistencyValidator:
    """
    Validates model configuration consistency across:
    ProviderProfile.default_model -> Runtime Selected Model -> Dashboard Model -> Provider Plugin Model
    """

    @classmethod
    def validate_consistency(cls) -> ProviderConsistencyReport:
        profiles = ProviderRegistry.list_registered_profiles()
        dashboard_snapshot = RuntimeDashboard.get_snapshot()
        dash_map = {
            p["provider_id"].lower(): p.get("current_model", "")
            for p in dashboard_snapshot.get("providers", [])
        }

        items: List[ProviderConsistencyItem] = []
        passed_cnt = 0
        failed_cnt = 0

        for prof in profiles:
            p_id = prof.provider_id.lower()
            expected = prof.default_model or ""
            runtime_m = ProviderModel.resolve_model(p_id)
            dashboard_m = dash_map.get(p_id, prof.default_model or "")
            cfg = ProviderConfigCenter.get_provider_config(p_id)
            plugin_m = cfg.default_model

            is_consistent = (
                expected == runtime_m == dashboard_m == plugin_m
            )
            status = "PASS" if is_consistent else "FAIL"

            if is_consistent:
                passed_cnt += 1
            else:
                failed_cnt += 1

            items.append(ProviderConsistencyItem(
                provider=p_id,
                expected_model=expected,
                runtime_model=runtime_m,
                dashboard_model=dashboard_m,
                plugin_model=plugin_m,
                status=status
            ))

        overall = "PASS" if (failed_cnt == 0 and len(profiles) > 0) else "FAIL"

        return ProviderConsistencyReport(
            overall_status=overall,
            total_providers=len(profiles),
            passed_providers=passed_cnt,
            failed_providers=failed_cnt,
            details=items
        )
