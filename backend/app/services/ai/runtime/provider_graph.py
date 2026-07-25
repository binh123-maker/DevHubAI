import json
from typing import Dict, Any
from app.services.ai.runtime.provider_capability import DEFAULT_CAPABILITY_CHAINS

class ProviderGraph:
    @staticmethod
    def generate_mermaid() -> str:
        lines = [
            "graph TD",
            "    Sub[Capability Engine] -->|Resolves| RoutingMatrix[Capability Routing Matrix]"
        ]
        for cap, providers in DEFAULT_CAPABILITY_CHAINS.items():
            cap_node = f"Cap_{cap.value}"
            lines.append(f"    RoutingMatrix --> {cap_node}[Capability: {cap.value}]")
            for idx, p in enumerate(providers):
                p_node = f"P_{p}"
                lines.append(f"    {cap_node} -->|Priority {idx+1}| {p_node}[Provider: {p}]")
        return "\n".join(lines)

    @staticmethod
    def generate_json() -> str:
        graph_dict = {
            cap.value: providers
            for cap, providers in DEFAULT_CAPABILITY_CHAINS.items()
        }
        return json.dumps({"capability_routing_graph": graph_dict}, indent=2)
