import os
import sys
import subprocess
import pytest

@pytest.fixture
def cli_env():
    env = dict(os.environ)
    backend_dir = os.path.abspath("backend") if os.path.exists("backend") else os.path.abspath(".")
    env["PYTHONPATH"] = backend_dir + os.pathsep + env.get("PYTHONPATH", "")
    return env

def get_script_path(rel_path):
    if os.path.exists(rel_path):
        return rel_path
    if os.path.exists(os.path.join("backend", rel_path)):
        return os.path.join("backend", rel_path)
    return rel_path

def test_manage_ai_cli_list_providers(cli_env):
    script = get_script_path("manage_ai.py")
    res = subprocess.run([sys.executable, script, "list-providers"], capture_output=True, text=True, env=cli_env)
    assert res.returncode == 0
    assert "Total Registered Providers" in res.stdout

def test_manage_ai_cli_switch_policy(cli_env):
    script = get_script_path("manage_ai.py")
    res = subprocess.run([sys.executable, script, "switch-policy", "cheap"], capture_output=True, text=True, env=cli_env)
    assert res.returncode == 0
    assert "Switched active policy" in res.stdout

def test_manage_ai_cli_validate(cli_env):
    script = get_script_path("manage_ai.py")
    res = subprocess.run([sys.executable, script, "validate"], capture_output=True, text=True, env=cli_env)
    assert res.returncode == 0
    assert "system_valid" in res.stdout
