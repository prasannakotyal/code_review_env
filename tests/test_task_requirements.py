from collections import Counter
from pathlib import Path
import re

from inference import MAX_STEPS_BY_TASK
from models import IssueType, TaskName
from server.my_env_environment import (
    BUG_SNIPPETS,
    FULL_REVIEW_SNIPPETS,
    MyEnvironment,
    STYLE_SNIPPETS,
)


def _line_count(code: str) -> int:
    return len(code.splitlines())


def _overlap(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
    return not (a_end < b_start or b_end < a_start)


def test_snippet_set_sizes_are_in_target_range() -> None:
    assert 20 <= len(STYLE_SNIPPETS) <= 25
    assert 20 <= len(BUG_SNIPPETS) <= 25
    assert 20 <= len(FULL_REVIEW_SNIPPETS) <= 25


def test_style_snippets_match_easy_requirements() -> None:
    for snippet in STYLE_SNIPPETS.values():
        issues = snippet["issues"]
        code_lines = _line_count(snippet["code"])

        assert 1 <= len(issues) <= 2

        for issue in issues:
            assert issue.issue_type == IssueType.STYLE
            assert 1 <= issue.line_start <= issue.line_end <= code_lines


def test_bug_snippets_match_medium_requirements() -> None:
    for snippet in BUG_SNIPPETS.values():
        issues = snippet["issues"]
        code_lines = _line_count(snippet["code"])

        assert 2 <= len(issues) <= 3

        for issue in issues:
            assert issue.issue_type == IssueType.BUG
            assert 1 <= issue.line_start <= issue.line_end <= code_lines


def test_full_review_snippets_match_hard_requirements() -> None:
    for snippet in FULL_REVIEW_SNIPPETS.values():
        issues = snippet["issues"]
        code_lines = _line_count(snippet["code"])
        issue_counts = Counter(issue.issue_type for issue in issues)

        assert 3 <= len(issues) <= 4
        assert issue_counts[IssueType.STYLE] >= 1
        assert issue_counts[IssueType.BUG] >= 1
        assert issue_counts[IssueType.SECURITY] >= 1

        for issue in issues:
            assert 1 <= issue.line_start <= issue.line_end <= code_lines
            if issue.issue_type == IssueType.SECURITY:
                assert issue.fix_suggestion is not None
                assert issue.fix_suggestion.strip() != ""


def test_no_overlapping_ranges_for_same_issue_type() -> None:
    for snippet_set in (STYLE_SNIPPETS, BUG_SNIPPETS, FULL_REVIEW_SNIPPETS):
        for snippet in snippet_set.values():
            issues = snippet["issues"]
            for i in range(len(issues)):
                left = issues[i]
                for j in range(i + 1, len(issues)):
                    right = issues[j]
                    if left.issue_type != right.issue_type:
                        continue
                    assert not _overlap(
                        left.line_start,
                        left.line_end,
                        right.line_start,
                        right.line_end,
                    )


def test_max_steps_match_requirements_across_files() -> None:
    expected = {
        TaskName.STYLE_CHECK: 7,
        TaskName.BUG_HUNT: 12,
        TaskName.FULL_REVIEW: 18,
    }

    assert MyEnvironment.MAX_STEPS == expected
    assert MAX_STEPS_BY_TASK == expected

    openenv_text = Path("openenv.yaml").read_text()
    assert re.search(r"id:\s*style_check[\s\S]*?max_steps:\s*7", openenv_text)
    assert re.search(r"id:\s*bug_hunt[\s\S]*?max_steps:\s*12", openenv_text)
    assert re.search(r"id:\s*full_review[\s\S]*?max_steps:\s*18", openenv_text)
