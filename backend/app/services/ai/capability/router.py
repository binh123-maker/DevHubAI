import logging
from typing import List, Dict, Any, Tuple
from app.services.ai.capability.types import AICapability, AIRole, TASK_TO_ROLE_CAPABILITY_MAP
from app.services.ai.task.task_type import TaskType
from app.services.ai.config.capabilities_config import DEFAULT_CAPABILITY_PRIORITIES

logger = logging.getLogger(__name__)

class CapabilityRouter:
    @classmethod
    def resolve_role_and_capability(cls, task_type: TaskType) -> Tuple[AIRole, AICapability]:
        """
        Maps a classified TaskType to its corresponding AIRole and AICapability.
        """
        role, capability = TASK_TO_ROLE_CAPABILITY_MAP.get(
            task_type,
            (AIRole.CHAT_AI, AICapability.CHAT)
        )
        return role, capability

    @classmethod
    def get_candidate_providers(cls, capability: AICapability) -> List[Dict[str, str]]:
        """
        Returns the ordered priority list of candidate providers and models for a given capability.
        """
        cap_key = capability.value if isinstance(capability, AICapability) else str(capability)
        candidates = DEFAULT_CAPABILITY_PRIORITIES.get(
            cap_key,
            DEFAULT_CAPABILITY_PRIORITIES["chat"]
        )
        logger.debug(f"[CapabilityRouter] Capability '{cap_key}' resolved to candidate list: {candidates}")
        return candidates
