import pytest
from app.services.ai.runtime.runtime_timeline import RuntimeTimeline

@pytest.fixture(autouse=True)
def reset_timeline_state():
    RuntimeTimeline.reset()
    yield
    RuntimeTimeline.reset()

def test_runtime_timeline_tracking():
    RuntimeTimeline.start(task_type="CHAT", capability="chat")
    RuntimeTimeline.add_step("Provider Selector", {"selected": "groq"})

    steps = RuntimeTimeline.get_last_timeline()
    assert len(steps) == 3
    assert steps[0]["step"] == "Gateway"
    assert steps[1]["step"] == "Task Analyzer"
    assert steps[2]["step"] == "Provider Selector"

    json_str = RuntimeTimeline.generate_json()
    assert "Gateway" in json_str

    md_str = RuntimeTimeline.generate_markdown()
    assert "# Request Execution Timeline" in md_str
