from inference import load_config, log_end, log_start, log_step


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


def test_load_config_falls_back_to_hf_token(monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.setenv("HF_TOKEN", "local-key")
    monkeypatch.delenv("MY_ENV_TASK", raising=False)

    config = load_config()

    assert config.api_key == "local-key"
