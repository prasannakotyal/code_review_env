from inference import (
    InferenceConfig,
    ensure_proxy_call,
    load_config,
    log_end,
    log_start,
    log_step,
)
from models import TaskName


def test_log_start_format(capsys):
    log_start(task="style_check", env="my_env", model="Qwen/Qwen2.5-7B-Instruct")
    captured = capsys.readouterr()
    assert (
        captured.out
        == "[START] task=style_check env=my_env model=Qwen/Qwen2.5-7B-Instruct\n"
    )


def test_log_step_format(capsys):
    log_step(
        step=2,
        action="style@4@Variable_should_use_snake_case",
        reward=0.33,
        done=False,
        error=None,
    )
    captured = capsys.readouterr()
    assert (
        captured.out
        == "[STEP] step=2 action=style@4@Variable_should_use_snake_case reward=0.33 done=false error=null\n"
    )


def test_log_end_format(capsys):
    log_end(success=True, steps=3, score=0.99, rewards=[0.33, 0.33, 0.34])
    captured = capsys.readouterr()
    assert (
        captured.out == "[END] success=true steps=3 score=0.99 rewards=0.33,0.33,0.34\n"
    )


def test_load_config_prefers_api_key(monkeypatch):
    monkeypatch.setenv("API_KEY", "validator-key")
    monkeypatch.setenv("HF_TOKEN", "local-key")
    monkeypatch.setenv("API_BASE_URL", "https://proxy.example/v1")
    monkeypatch.setenv("MODEL_NAME", "test-model")
    monkeypatch.delenv("MY_ENV_TASK", raising=False)

    config = load_config()

    assert config.api_key == "validator-key"
    assert config.api_base_url == "https://proxy.example/v1"
    assert config.model_name == "test-model"


def test_ensure_proxy_call_uses_client_completion_api():
    calls = []

    class DummyCompletions:
        def create(self, **kwargs):
            calls.append(kwargs)
            return object()

    class DummyChat:
        def __init__(self):
            self.completions = DummyCompletions()

    class DummyClient:
        def __init__(self):
            self.chat = DummyChat()

    config = InferenceConfig(
        api_base_url="https://proxy.example/v1",
        api_key="validator-key",
        model_name="test-model",
        env_base_url="https://env.example",
        task_name=TaskName.STYLE_CHECK,
        benchmark="my_env",
        max_steps=7,
        temperature=0.0,
        max_tokens=300,
    )

    ensure_proxy_call(client=DummyClient(), config=config)

    assert len(calls) == 1
    assert calls[0]["model"] == "test-model"
    assert calls[0]["max_tokens"] == 4
