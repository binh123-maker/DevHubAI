#!/usr/bin/env python
import os
import sys
import json
import argparse

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.ai.config import ProviderConfigCenter, ConfigurationValidator
from app.services.ai.runtime import (
    ProviderRegistry,
    ProviderManifest,
    ProviderStatistics,
    RuntimeTimeline,
    RuntimeAnalytics,
    ProviderRecommendationEngine,
    TraceStore,
    RuntimeDashboard
)
from app.services.ai.policy import PolicyEngine
from app.services.ai.health.monitor import HealthMonitor

def main():
    parser = argparse.ArgumentParser(description="DevHub AI Operations Center CLI (ai_runtime.py)")
    parser.add_argument("command", choices=[
        "list", "health", "ranking", "trace", "analytics", "providers", "recommend", "validate", "timeline", "manifest"
    ], help="Command to execute")
    parser.add_argument("--capability", type=str, default="chat", help="Target capability (chat, reasoning, etc.)")
    parser.add_argument("--trace_id", type=str, default=None, help="Trace ID for detail lookup")

    args = parser.parse_args()
    cmd = args.command.lower()

    if cmd in ("list", "providers"):
        profiles = ProviderConfigCenter.list_profiles()
        print(f"Total Registered Providers: {len(profiles)}")
        for p in profiles:
            status = "ENABLED" if p.enabled else "DISABLED"
            print(f" - [{p.provider_id}] {p.display_name} | Group: {p.group} | Status: {status} | Health: {p.health_status}")

    elif cmd == "health":
        print(json.dumps(HealthMonitor.get_health_snapshot(), indent=2))

    elif cmd == "ranking":
        rankings = ProviderRecommendationEngine.recommend_for_capability(args.capability)
        print(json.dumps(rankings, indent=2))

    elif cmd == "recommend":
        recs = ProviderRecommendationEngine.recommend_all()
        print(json.dumps(recs, indent=2))

    elif cmd == "trace":
        if args.trace_id:
            t = TraceStore.get_trace(args.trace_id)
            print(json.dumps(t, indent=2) if t else f"Trace '{args.trace_id}' not found.")
        else:
            print(json.dumps(TraceStore.get_recent_traces(limit=20), indent=2))

    elif cmd == "analytics":
        print(json.dumps(RuntimeAnalytics.get_analytics_report(), indent=2))

    elif cmd == "validate":
        print(json.dumps(ConfigurationValidator.validate_all(), indent=2))

    elif cmd == "timeline":
        print(RuntimeTimeline.generate_markdown())

    elif cmd == "manifest":
        print(ProviderManifest.generate_json())

if __name__ == "__main__":
    main()
