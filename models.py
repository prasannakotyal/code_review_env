from typing import List, Optional
from enum import Enum

from pydantic import Field, BaseModel

try:
    from openenv.core.env_server.types import Action, Observation, State
except ImportError:
    from openenv.core.env_server.interfaces import Action, Observation, State


class IssueType(str, Enum):
    STYLE = "style"
    BUG = "bug"
    SECURITY = "security"


class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"


class TaskName(str, Enum):
    STYLE_CHECK = "style_check"
    BUG_HUNT = "bug_hunt"
    FULL_REVIEW = "full_review"


class Issue(BaseModel):
    issue_type: IssueType
    description: str
    line_start: int
    line_end: int
    fix_suggestion: Optional[str] = None


class FoundIssue(BaseModel):
    issue_type: IssueType
    description: str
    line_number: int
    fix_suggestion: Optional[str] = None
    is_correct: bool = False


class CodeReviewAction(Action):
    issue_type: IssueType = Field(description="Type of issue being reported")
    description: str = Field(description="Description of the issue found")
    line_number: int = Field(description="Line number where issue is located")
    fix_suggestion: Optional[str] = Field(
        default=None, description="Suggested fix (for hard mode)"
    )


class CodeReviewObservation(Observation):
    done: bool = Field(default=False, description="Whether episode is complete")
    reward: Optional[float] = Field(default=None, description="Reward value")
    code_snippet: str = Field(description="Current code snippet")
    issues_found: List[FoundIssue] = Field(
        default_factory=list, description="Issues found so far"
    )
    issues_remaining: int = Field(description="Total issues remaining to find")
    step_count: int = Field(default=0, description="Current step count")
    message: str = Field(default="", description="Feedback on last action")
    task_name: TaskName = Field(description="Current task difficulty")
    language: Language = Field(description="Programming language of snippet")


class CodeReviewState(State):
    episode_id: Optional[str] = None
    step_count: int = 0
    target_snippet_id: str = ""
    ground_truth_issues: List[Issue] = Field(default_factory=list)
    current_score: float = 0.0
    task_name: TaskName = TaskName.STYLE_CHECK
    language: Language = Language.PYTHON
    code_snippet: str = ""
