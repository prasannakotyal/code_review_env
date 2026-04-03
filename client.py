try:
    from openenv.core.env_client import EnvClient
    from openenv.core.client_types import StepResult
except ImportError:
    from openenv.core.env_client import EnvClient
    from openenv.core.client_types import StepResult

try:
    from models import (
        CodeReviewAction,
        CodeReviewObservation,
        CodeReviewState,
        FoundIssue,
        IssueType,
        TaskName,
        Language,
        Issue,
    )
except ImportError:
    from .models import (
        CodeReviewAction,
        CodeReviewObservation,
        CodeReviewState,
        FoundIssue,
        IssueType,
        TaskName,
        Language,
        Issue,
    )


class MyEnv(EnvClient[CodeReviewAction, CodeReviewObservation, CodeReviewState]):
    def _step_payload(self, action: CodeReviewAction) -> dict:
        return {
            "issue_type": action.issue_type.value,
            "description": action.description,
            "line_number": action.line_number,
            "fix_suggestion": action.fix_suggestion,
        }

    def _parse_result(self, payload: dict) -> StepResult:
        obs_data = payload.get("observation", {})

        issues_found = []
        for issue_data in obs_data.get("issues_found", []):
            issues_found.append(
                FoundIssue(
                    issue_type=IssueType(issue_data.get("issue_type", "style")),
                    description=issue_data.get("description", ""),
                    line_number=issue_data.get("line_number", 0),
                    fix_suggestion=issue_data.get("fix_suggestion"),
                    is_correct=issue_data.get("is_correct", False),
                )
            )

        return StepResult(
            observation=CodeReviewObservation(
                done=payload.get("done", False),
                reward=payload.get("reward"),
                code_snippet=obs_data.get("code_snippet", ""),
                issues_found=issues_found,
                issues_remaining=obs_data.get("issues_remaining", 0),
                step_count=obs_data.get("step_count", 0),
                message=obs_data.get("message", ""),
                task_name=TaskName(obs_data.get("task_name", "style_check")),
                language=Language(obs_data.get("language", "python")),
            ),
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: dict) -> CodeReviewState:
        ground_truth = []
        for issue_data in payload.get("ground_truth_issues", []):
            ground_truth.append(
                Issue(
                    issue_type=IssueType(issue_data.get("issue_type", "style")),
                    description=issue_data.get("description", ""),
                    line_start=issue_data.get("line_start", 0),
                    line_end=issue_data.get("line_end", 0),
                    fix_suggestion=issue_data.get("fix_suggestion"),
                )
            )

        return CodeReviewState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            target_snippet_id=payload.get("target_snippet_id", ""),
            ground_truth_issues=ground_truth,
            current_score=payload.get("current_score", 0.0),
            task_name=TaskName(payload.get("task_name", "style_check")),
            language=Language(payload.get("language", "python")),
            code_snippet=payload.get("code_snippet", ""),
        )
