import pytest

from models import (
    CodeReviewAction,
    CodeReviewObservation,
    CodeReviewState,
    IssueType,
)
from server.my_env_environment import MyEnvironment


def test_imports():
    assert CodeReviewAction is not None
    assert CodeReviewObservation is not None
    assert CodeReviewState is not None
    assert MyEnvironment is not None


def test_environment_creation():
    env = MyEnvironment()
    assert env is not None


def test_environment_reset():
    env = MyEnvironment()
    obs = env.reset(task_name="style_check")

    assert obs is not None
    assert obs.code_snippet != ""
    assert obs.issues_remaining > 0
    assert obs.done is False


def test_environment_step():
    env = MyEnvironment()
    obs = env.reset(task_name="style_check")

    action = CodeReviewAction(
        issue_type=IssueType.STYLE,
        description="Function name should use snake_case",
        line_number=1,
    )

    result = env.step(action)

    assert result is not None
    assert result.step_count == 1
    assert 0.0 <= result.reward <= 1.0


def test_rewards_stay_in_normalized_range():
    env = MyEnvironment()
    env.reset(task_name="style_check")

    false_positive = env.step(
        CodeReviewAction(
            issue_type=IssueType.STYLE,
            description="Completely wrong issue",
            line_number=99,
        )
    )
    assert false_positive.reward == 0.0

    correct = env.step(
        CodeReviewAction(
            issue_type=IssueType.STYLE,
            description="Function name should use snake_case",
            line_number=1,
        )
    )
    assert 0.0 <= correct.reward <= 1.0
    assert 0.0 <= env.state.current_score <= 1.0
