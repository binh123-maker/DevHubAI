#!/usr/bin/env python
import os
import sys
import json
import argparse

# Ensure backend path is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app.services.ai.config import ProviderConfigCenter, ConfigurationValidator
from app.services.ai.runtime import (
    ProviderRegistry,
    ProviderManifest,
    ProviderStatistics,
    ProviderSandbox,
    RuntimeTimeline,
    RecommendationEngine,
    RuntimeDashboard
)
from app.services.ai.policy import PolicyEngine
from app.services.ai.health.monitor import HealthMonitor

def main():
    parser = argparse.ArgumentParser(description="DevHub AI Platform Runtime CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available Commands")

    subparsers.add_parser("list-providers", help="List registered AI providers")
    
    show_p = subparsers.add_parser("show-provider", help="Show provider profile details")
    show_p.add_argument("provider", type=str, help="Provider ID (e.g. groq, openai)")

    subparsers.add_parser("show-policy", help="Show active runtime policy profile")
    
    switch_p = subparsers.add_parser("switch-policy", help="Switch active policy profile")
    switch_p.add_argument("policy", type=str, help="Policy name (development, production, cheap, reasoning, coding)")

    subparsers.add_parser("health", help="Show health snapshot of all providers")
    subparsers.add_parser("stats", help="Show runtime execution statistics")
    subparsers.add_parser("manifest", help="Generate Provider Manifest JSON")
    subparsers.add_parser("dashboard", help="Generate Runtime Dashboard JSON snapshot")
    subparsers.add_parser("reload", help="Reload all provider configurations")
    
    enable_p = subparsers.add_parser("enable", help="Enable an AI provider")
    enable_p.add_argument("provider", type=str, help="Provider ID")

    disable_p = subparsers.add_parser("disable", help="Disable an AI provider")
    disable_p.add_argument("provider", type=str, help="Provider ID")

    rec_p = subparsers.add_parser("recommend", help="Recommend top provider for capability")
    rec_p.add_argument("capability", type=str, default="chat", nargs="?", help="Capability (chat, reasoning, doc_qa)")

    sandbox_p = subparsers.add_parser("sandbox", help="Run provider sandbox test")
    sandbox_p.add_argument("--provider", type=str, default="groq", help="Provider ID")
    sandbox_p.add_argument("--model", type=str, default=None, help="Model override")
    sandbox_p.add_argument("--prompt", type=str, default="Hello AI", help="Test prompt")

    subparsers.add_parser("validate", help="Validate runtime configurations")
    subparsers.add_parser("timeline", help="Show last request execution timeline")

    args = parser.parse_args()

    if args.command == "list-providers":
        profiles = ProviderConfigCenter.list_profiles()
        print(f"Total Registered Providers: {len(profiles)}")
        for p in profiles:
            status = "ENABLED" if p.enabled else "DISABLED"
            print(f" - [{p.provider_id}] {p.display_name} | Priority: {p.priority} | Status: {status} | Health: {p.health_status}")

    elif args.command == "show-provider":
        p = ProviderConfigCenter.get_profile(args.provider)
        if p:
            print(json.dumps(p.model_dump(), indent=2))
        else:
            print(f"Provider '{args.provider}' not found.")

    elif args.command == "show-policy":
        print(f"Active Policy: {PolicyEngine.get_policy()}")
        profile = PolicyEngine.get_current_profile()
        if profile:
            print(json.dumps(profile.model_dump(), indent=2))

    elif args.command == "switch-policy":
        success = PolicyEngine.set_policy(args.policy)
        if success:
            print(f"Switched active policy to '{args.policy}'")
        else:
            print(f"Failed to switch policy to '{args.policy}'")

    elif args.command == "health":
        print(json.dumps(HealthMonitor.get_health_snapshot(), indent=2))

    elif args.command == "stats":
        print(json.dumps(ProviderStatistics.get_summary(), indent=2))

    elif args.command == "manifest":
        print(ProviderManifest.generate_json())

    elif args.command == "dashboard":
        print(json.dumps(RuntimeDashboard.get_snapshot(), indent=2))

    elif args.command == "reload":
        ProviderConfigCenter.reload()
        print("Successfully reloaded all provider profiles and configurations.")

    elif args.command == "enable":
        ProviderConfigCenter.enable(args.provider)
        print(f"Enabled provider '{args.provider}'")

    elif args.command == "disable":
        ProviderConfigCenter.disable(args.provider)
        print(f"Disabled provider '{args.provider}'")

    elif args.command == "recommend":
        rec = RecommendationEngine.recommend_provider(args.capability)
        print(json.dumps(rec, indent=2))

    elif args.command == "sandbox":
        res = ProviderSandbox.run(provider=args.provider, model=args.model, prompt=args.prompt)
        print(json.dumps(res, indent=2))

    elif args.command == "validate":
        rep = ConfigurationValidator.validate_all()
        print(json.dumps(rep, indent=2))

    elif args.command == "timeline":
        print(RuntimeTimeline.generate_markdown())

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
