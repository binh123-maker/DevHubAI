import os
import re
from typing import Dict, Any, List

class ProviderDeadCodeScanner:
    """
    Dead code and legacy pattern scanner for the backend codebase.
    Checks for legacy patterns like direct OpenAI imports in business logic,
    scattered API key accesses, and hardcoded models.
    """

    @classmethod
    def scan_directory(cls, base_dir: str) -> Dict[str, Any]:
        direct_env_reads = 0
        direct_provider_instantiations = 0
        hardcoded_model_strings = 0
        scanned_files = 0
        file_issues: List[dict] = []

        patterns_env = [r"settings\.openai_api_key", r"settings\.groq_api_key", r"settings\.gemini_api_key", r"os\.getenv\([\"']OPENAI_API_KEY"]
        patterns_instantiation = [r"\bOpenAI\(", r"\bgoogle\.generativeai\.", r"\bGroq\("]
        patterns_hardcoded_models = [r"\"gpt-4o\"", r"\"gemini-2\.5-flash\"", r"\"llama-3\.3-70b-versatile\""]

        for root, _, files in os.walk(base_dir):
            if "__pycache__" in root or ".pytest_cache" in root:
                continue
            for file in files:
                if file.endswith(".py"):
                    scanned_files += 1
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = f.read()

                        # Skip scanner file itself
                        if "provider_dead_code_scanner.py" in file:
                            continue

                        e_matches = sum(len(re.findall(pat, content)) for pat in patterns_env)
                        i_matches = sum(len(re.findall(pat, content)) for pat in patterns_instantiation)
                        m_matches = sum(len(re.findall(pat, content)) for pat in patterns_hardcoded_models)

                        direct_env_reads += e_matches
                        direct_provider_instantiations += i_matches
                        hardcoded_model_strings += m_matches

                        if e_matches > 0 or i_matches > 0:
                            file_issues.append({
                                "file": file,
                                "env_reads": e_matches,
                                "direct_instantiations": i_matches,
                                "hardcoded_models": m_matches
                            })
                    except Exception:
                        pass

        return {
            "scanned_files": scanned_files,
            "direct_env_reads": direct_env_reads,
            "direct_provider_instantiations": direct_provider_instantiations,
            "hardcoded_model_strings": hardcoded_model_strings,
            "issues": file_issues
        }
