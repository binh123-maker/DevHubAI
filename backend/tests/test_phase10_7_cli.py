import os
import sys
import subprocess
import pytest

@pytest.fixture
def cli_env():
    env = dict(os.environ)
    backend_dir = os.path.abspath("backend")
    env["PYTHONPATH"] = backend_dir + os.pathsep + env.get("PYTHONPATH", "")
    return env

def test_manage_ai_cli_list_providers(cli_env):
    res = subprocess.run([sys.executable, "backend/manage_ai.py", "list-providers"], capture_output=True, text=True, env=cli_env)
    assert res.returncode == 0
    assert "Total Registered Providers" in res.stdout
    assert "openai" in res.stdout or "groq" in res.stdout

def test_manage_ai_cli_switch_policy(cli_env):
    res = subprocess.run([sys.executable, "backend/manage_ai.py", "switch-policy", "cheap"], capture_output=True, text=True, env=cli_env)
    assert res.returncode == 0
    assert "Switched active policy to 'cheap'" in res.stdout

def test_manage_ai_cli_validate(cli_env):
    res = subprocess.run([sys.executable, "backend/manage_ai.py", "validate"], capture_output=True, text=True, env=cli_env)
    assert res.returncode == 0
    assert "system_valid" in res.stdout
