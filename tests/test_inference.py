from inference import log_end, log_start, log_step


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
