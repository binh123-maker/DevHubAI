import logging
from typing import Dict, List, Optional
from app.services.ai.runtime.provider_capability import Capability, DEFAULT_CAPABILITY_CHAINS

logger = logging.getLogger(__name__)

class ProviderCapabilityMatrix:
    _priority_overrides: Dict[str, List[str]] = {}

    @classmethod
    def set_priority_chain(cls, capability: str, provider_chain: List[str]) -> None:
        c_key = capability.lower()
        cls._priority_overrides[c_key] = [p.lower() for p in provider_chain]
        logger.info(f"[ProviderCapabilityMatrix] Set priority chain override for capability '{c_key}': {provider_chain}")

    @classmethod
    def get_priority_chain(cls, capability: str) -> List[str]:
        """
        Returns the candidate provider chain for a given capability.
        Capability matrix is extremely easy to edit in one place or override externally.
        """
        c_key = capability.lower()
        if c_key in cls._priority_overrides:
            return cls._priority_overrides[c_key]

        # Convert str to Enum if possible
        try:
            cap_enum = Capability(c_key)
            if cap_enum in DEFAULT_CAPABILITY_CHAINS:
                return DEFAULT_CAPABILITY_CHAINS[cap_enum]
        except ValueError:
            pass

        return DEFAULT_CAPABILITY_CHAINS.get(Capability.CHAT, ["openai", "groq", "gemini", "ollama"])

    @classmethod
    def get_matrix_snapshot(cls) -> Dict[str, List[str]]:
        snapshot = {
            cap.value: list(chain)
            for cap, chain in DEFAULT_CAPABILITY_CHAINS.items()
        }
        for cap_key, chain in cls._priority_overrides.items():
            snapshot[cap_key] = list(chain)
        return snapshot

    @classmethod
    def reset(cls) -> None:
        cls._priority_overrides.clear()
