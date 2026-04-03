import pytest


def test_imports():
    from code_review_env.models import (
        CodeReviewAction,
        CodeReviewObservation,
        CodeReviewState,
    )
    from code_review_env.server.environment import CodeReviewEnvironment

    assert CodeReviewAction is not None
    assert CodeReviewObservation is not None
    assert CodeReviewState is not None
    assert CodeReviewEnvironment is not None


def test_environment_creation():
    from code_review_env.server.environment import CodeReviewEnvironment

    env = CodeReviewEnvironment()
    assert env is not None


def test_environment_reset():
    from code_review_env.server.environment import CodeReviewEnvironment

    env = CodeReviewEnvironment()
    obs = env.reset(task_name="style_check")

    assert obs is not None
    assert obs.code_snippet != ""
    assert obs.issues_remaining > 0
    assert obs.done is False


def test_environment_step():
    from code_review_env.models import CodeReviewAction, IssueType
    from code_review_env.server.environment import CodeReviewEnvironment

    env = CodeReviewEnvironment()
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
    from code_review_env.models import CodeReviewAction, IssueType
    from code_review_env.server.environment import CodeReviewEnvironment

    env = CodeReviewEnvironment()
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
