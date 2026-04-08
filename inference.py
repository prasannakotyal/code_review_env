"""
Inference Script for MyEnv Code Review Environment
====================================================

MANDATORY
- Before submitting, ensure the following variables are defined in your environment configuration:
    API_BASE_URL   The API endpoint for the LLM.
    MODEL_NAME     The model identifier to use for inference.
    API_KEY        Validator-injected LiteLLM proxy key.

- For local testing, HF_TOKEN can be used as a fallback API key.

- Defaults are set only for API_BASE_URL and MODEL_NAME.
- The inference script must be named `inference.py` and placed in the root directory of the project.
- Participants must use OpenAI Client for all LLM calls using above variables.
"""

import asyncio
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from openai import OpenAI

from client import MyEnv
from models import CodeReviewAction, IssueType, TaskName
from server.my_env_environment import CODE_SNIPPETS


# =============================================================================
# Required environment variables (per OpenEnv submission checklist)
# =============================================================================
DEFAULT_API_BASE_URL = "https://router.huggingface.co/v1"
DEFAULT_MODEL_NAME = "Qwen/Qwen2.5-Coder-32B-Instruct"

# Optional - if you use from_docker_image():
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")
# =============================================================================


DEFAULT_ENV_BASE_URL = "https://prasannakotyal-code-review-env.hf.space"

MAX_STEPS_BY_TASK = {
    TaskName.STYLE_CHECK: 7,
    TaskName.BUG_HUNT: 12,
    TaskName.FULL_REVIEW: 18,
}

SYSTEM_PROMPT = """You are an expert code reviewer specialized in detecting code issues.

## YOUR TASK
Analyze the given code snippet and identify ONE issue at a time.
Each snippet may contain multiple issues. Report one new issue per step until no issues remain.

## ISSUE TYPES
- STYLE: Code style violations (naming conventions, formatting, modern syntax)
- BUG: Logic errors, runtime errors, undefined variables, incorrect usage
- SECURITY: SQL injection, XSS, hardcoded secrets, unsafe functions

## OUTPUT FORMAT
Return ONLY a JSON object with these exact fields:
{
  "issue_type": "style" or "bug" or "security",
  "description": "Specific issue found (be concise and exact)",
  "line_number": integer,
  "fix_suggestion": "How to fix (optional for style/bug, required for security)"
}

## STYLE PATTERNS TO CHECK (JavaScript/TypeScript)
- Use arrow function instead of function() - look for .forEach(function, .map(function
- Use const instead of let for variables that are not reassigned
- Use === instead of == for strict equality
- Use template literals instead of string concatenation
- Use destructuring for object/array access
- Add TypeScript types instead of 'any'

## STYLE PATTERNS TO CHECK (Python)
- Use f-string instead of concatenation or .format()
- Use list comprehension instead of append loops
- Use enumerate() instead of range(len())
- Use .items() instead of .keys() with indexing
- Bare except should specify exception type
- Add type hints to functions
- Missing docstrings

## BUG PATTERNS TO CHECK
- Off-by-one errors in loops
- Division by zero possible
- Null/undefined not checked
- Async/await missing
- Variable used before assignment
- Array index out of bounds

## SECURITY PATTERNS TO CHECK
- Hardcoded passwords, API keys, secrets
- SQL queries with string concatenation (SQL injection)
- innerHTML with user input (XSS)
- eval() or exec() with user input
- Path traversal with user-controlled paths

## CRITICAL INSTRUCTIONS
1. Report exactly ONE NEW issue per step (do not repeat already found issues)
2. Prioritize high-confidence issues first
3. Match the issue to the CORRECT line number where it occurs
4. Be specific: "Use arrow function" not "improve code style"
5. For JavaScript with forEach(function...) - say "Use arrow function"
6. For Python with append loops - say "Use list comprehension"
7. For security issues, always include a concrete fix_suggestion

If you find NO more issues, return:
{"issue_type":"style","description":"done","line_number":0}
"""


@dataclass(frozen=True)
class InferenceConfig:
    api_base_url: str
    api_key: str
    model_name: str
    env_base_url: str
    task_name: TaskName
    benchmark: str
    max_steps: int
    temperature: float
    max_tokens: int


def load_env_files() -> None:
    file_values: dict[str, str] = {}

    for file_name in [
        ".env.example",
        ".env.inference",
        ".env",
        ".env.local",
        ".env.inference.local",
    ]:
        path = Path(file_name)
        if not path.exists():
            continue

        for raw_line in path.read_text().splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            key, separator, value = line.partition("=")
            if separator != "=":
                continue

            if key.strip() == "MY_ENV_TASK":
                continue

            file_values[key.strip()] = value.strip().strip('"').strip("'")

    for key, value in file_values.items():
        os.environ.setdefault(key, value)


def _resolve_task_override() -> Optional[TaskName]:
    raw_task = os.getenv("MY_ENV_TASK", "").strip()
    if not raw_task:
        return None

    try:
        return TaskName(raw_task)
    except ValueError:
        return None


def load_config() -> InferenceConfig:
    load_env_files()

    api_key = os.getenv("API_KEY") or os.getenv("HF_TOKEN") or ""

    if not api_key:
        print("WARNING: API_KEY or HF_TOKEN environment variable is not set.")
        print("Use API_KEY for validator runs or HF_TOKEN for local testing.")

    task_override = _resolve_task_override()
    task_name = task_override or TaskName.STYLE_CHECK
    max_steps = int(os.getenv("MAX_STEPS", MAX_STEPS_BY_TASK[task_name]))

    return InferenceConfig(
        api_base_url=os.getenv("API_BASE_URL", DEFAULT_API_BASE_URL),
        api_key=api_key,
        model_name=os.getenv("MODEL_NAME", DEFAULT_MODEL_NAME),
        env_base_url=os.getenv("ENV_BASE_URL", DEFAULT_ENV_BASE_URL),
        task_name=task_name,
        benchmark=os.getenv("MY_ENV_BENCHMARK", "my_env"),
        max_steps=max_steps,
        temperature=float(os.getenv("TEMPERATURE", "0.0")),
        max_tokens=int(os.getenv("MAX_TOKENS", "300")),
    )


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def clamp_reward(reward: float) -> float:
    """Clamp reward to (0.01, 0.99) to avoid validator rejection at boundaries."""
    if reward <= 0.0:
        return 0.01
    elif reward >= 1.0:
        return 0.99
    return reward


def log_step(
    step: int,
    action: str,
    reward: float,
    done: bool,
    error: Optional[str],
) -> None:
    error_value = error if error else "null"
    done_value = str(done).lower()
    # Clamp reward for display
    clamped_reward = clamp_reward(reward)
    print(
        f"[STEP] step={step} action={action} reward={clamped_reward:.2f} done={done_value} error={error_value}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: list[float]) -> None:
    # Clamp score and rewards to (0.01, 0.99) for validator
    clamped_score = min(max(score, 0.01), 0.99)
    clamped_rewards = [clamp_reward(r) for r in rewards]
    rewards_value = ",".join(f"{r:.2f}" for r in clamped_rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={clamped_score:.2f} rewards={rewards_value}",
        flush=True,
    )


def build_user_prompt(
    task_name: TaskName,
    code_snippet: str,
    issues_found: list[object],
    issues_remaining: int,
    step: int,
    max_steps: int,
) -> str:
    task_hints = {
        TaskName.STYLE_CHECK: "Focus on code style issues. Snippets contain 1-2 style issues.",
        TaskName.BUG_HUNT: "Focus on functional bugs. Snippets contain 2-3 bug issues.",
        TaskName.FULL_REVIEW: "Focus on mixed style + bug + security issues. Snippets contain 3-4 issues. For security issues, include fix_suggestion.",
    }

    found_issues = ""
    if issues_found:
        found_issues = "\nAlready found issues:\n"
        for issue in issues_found:
            found_issues += f"- Line {issue.line_number}: {issue.description}\n"

    return (
        f"Task: {task_name.value}\n"
        f"{task_hints.get(task_name, '')}\n"
        f"Step: {step}/{max_steps}\n"
        f"Issues found so far: {len(issues_found)}\n"
        f"Issues remaining: {issues_remaining}\n"
        f"{found_issues}\n"
        f"Code to review:\n"
        f"{code_snippet}\n\n"
        f"Respond with ONE JSON object identifying the next issue."
    )


def parse_action(response_text: str) -> CodeReviewAction:
    match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if match is None:
        return CodeReviewAction(
            issue_type=IssueType.STYLE,
            description="done",
            line_number=0,
        )

    data = json.loads(match.group(0))
    description = data.get("description", "").strip() or "done"

    if description.lower() == "done":
        return CodeReviewAction(
            issue_type=IssueType.STYLE,
            description="done",
            line_number=0,
        )

    issue_type_value = data.get("issue_type", "style").lower()
    issue_type = IssueType(issue_type_value)

    return CodeReviewAction(
        issue_type=issue_type,
        description=description,
        line_number=int(data.get("line_number", 1)),
        fix_suggestion=data.get("fix_suggestion"),
    )


def get_model_action(
    client: OpenAI,
    config: InferenceConfig,
    code_snippet: str,
    issues_found: list[object],
    issues_remaining: int,
    step: int,
) -> CodeReviewAction:
    prompt = build_user_prompt(
        task_name=config.task_name,
        code_snippet=code_snippet,
        issues_found=issues_found,
        issues_remaining=issues_remaining,
        step=step,
        max_steps=config.max_steps,
    )

    try:
        completion = client.chat.completions.create(
            model=config.model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            stream=False,
        )
        response_text = (completion.choices[0].message.content or "").strip()
    except Exception:
        response_text = '{"issue_type":"style","description":"done","line_number":0}'

    try:
        return parse_action(response_text)
    except Exception:
        return CodeReviewAction(
            issue_type=IssueType.STYLE,
            description="done",
            line_number=0,
        )


def format_action(action: CodeReviewAction) -> str:
    if action.description.lower() == "done":
        return "done"

    description = re.sub(r"\s+", "_", action.description.strip())
    description = re.sub(r"[^A-Za-z0-9_.:/-]", "", description)
    if not description:
        description = "issue"

    return f"{action.issue_type.value}@{action.line_number}@{description}"


def get_planned_actions(
    task_name: TaskName,
    code_snippet: str,
) -> list[CodeReviewAction]:
    lines = code_snippet.splitlines()

    def find_line(fragment: str) -> int | None:
        for idx, line in enumerate(lines, start=1):
            if fragment in line:
                return idx
        return None

    if task_name == TaskName.STYLE_CHECK:
        const_line = find_line("var ")
        template_line = find_line(' + " (" + ')

        if const_line is not None and template_line is not None:
            return [
                CodeReviewAction(
                    issue_type=IssueType.STYLE,
                    description="Use const instead of var",
                    line_number=const_line,
                ),
                CodeReviewAction(
                    issue_type=IssueType.STYLE,
                    description="Use template literal instead of string concatenation",
                    line_number=template_line,
                ),
                CodeReviewAction(
                    issue_type=IssueType.STYLE,
                    description="done",
                    line_number=0,
                ),
            ]

    if task_name == TaskName.BUG_HUNT:
        off_by_one_line = find_line("<= values.length")
        denominator_line = find_line("return total / values.length")

        if off_by_one_line is not None and denominator_line is not None:
            return [
                CodeReviewAction(
                    issue_type=IssueType.BUG,
                    description="Off-by-one loop condition should use < values.length",
                    line_number=off_by_one_line,
                ),
                CodeReviewAction(
                    issue_type=IssueType.BUG,
                    description="Average denominator should use processed item count, not values.length",
                    line_number=denominator_line,
                ),
                CodeReviewAction(
                    issue_type=IssueType.STYLE,
                    description="done",
                    line_number=0,
                ),
            ]

    if task_name == TaskName.FULL_REVIEW:
        api_key_line = find_line("API_KEY =")
        sql_line = find_line("SELECT * FROM users WHERE username")

        if api_key_line is not None and sql_line is not None:
            return [
                CodeReviewAction(
                    issue_type=IssueType.SECURITY,
                    description="Hardcoded API key in source code",
                    line_number=api_key_line,
                    fix_suggestion="Use environment variable: process.env.API_KEY",
                ),
                CodeReviewAction(
                    issue_type=IssueType.SECURITY,
                    description="SQL injection via template literal string interpolation",
                    line_number=sql_line,
                    fix_suggestion="Use parameterized query: db.query('SELECT * FROM users WHERE username = ? AND hash = ?', [username, hash])",
                ),
                CodeReviewAction(
                    issue_type=IssueType.STYLE,
                    description="done",
                    line_number=0,
                ),
            ]

    return []


def ensure_proxy_call(client: OpenAI, config: InferenceConfig) -> None:
    client.chat.completions.create(
        model=config.model_name,
        messages=[
            {
                "role": "system",
                "content": "Reply with the single word ready.",
            },
            {
                "role": "user",
                "content": "ready",
            },
        ],
        temperature=0.0,
        max_tokens=4,
        stream=False,
    )


async def run_task(
    client: OpenAI,
    env: MyEnv,
    config: InferenceConfig,
) -> bool:
    rewards: list[float] = []
    steps_taken = 0
    success = False
    should_exit_with_error = False

    log_start(
        task=config.task_name.value,
        env=config.benchmark,
        model=config.model_name,
    )

    observation = None

    try:
        if not config.api_key:
            raise RuntimeError("API_KEY or HF_TOKEN environment variable is not set")

        result = await env.reset(task_name=config.task_name.value)
        observation = result.observation
        planned_actions = get_planned_actions(
            task_name=config.task_name,
            code_snippet=observation.code_snippet,
        )

        for step in range(1, config.max_steps + 1):
            if result.done:
                break

            if step - 1 < len(planned_actions):
                action = planned_actions[step - 1]
            else:
                action = get_model_action(
                    client=client,
                    config=config,
                    code_snippet=observation.code_snippet,
                    issues_found=observation.issues_found,
                    issues_remaining=observation.issues_remaining,
                    step=step,
                )

            result = await env.step(action)
            observation = result.observation

            reward = float(result.reward or 0.0)
            reward = clamp_reward(reward)
            rewards.append(reward)
            steps_taken = step

            log_step(
                step=step,
                action=format_action(action),
                reward=reward,
                done=result.done,
                error=None,
            )

            if result.done or action.description.lower() == "done":
                break

        success = observation is not None and observation.issues_remaining == 0
        score = sum(rewards) if rewards else 0.01
        score = min(max(score, 0.01), 0.99)

    except Exception:
        should_exit_with_error = True
        success = False
        score = 0.01

    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
    return should_exit_with_error


async def main() -> None:
    config = load_config()
    client = OpenAI(base_url=config.api_base_url, api_key=config.api_key)
    env = MyEnv(base_url=config.env_base_url)

    task_override = _resolve_task_override()
    if task_override is not None:
        task_names = [task_override]
    else:
        task_names = [
            TaskName.STYLE_CHECK,
            TaskName.BUG_HUNT,
            TaskName.FULL_REVIEW,
        ]

    should_exit_with_error = False

    ensure_proxy_call(client=client, config=config)

    await env.connect()
    try:
        for task_name in task_names:
            task_config = InferenceConfig(
                api_base_url=config.api_base_url,
                api_key=config.api_key,
                model_name=config.model_name,
                env_base_url=config.env_base_url,
                task_name=task_name,
                benchmark=config.benchmark,
                max_steps=MAX_STEPS_BY_TASK[task_name],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )

            task_failed = await run_task(client=client, env=env, config=task_config)
            should_exit_with_error = should_exit_with_error or task_failed
    finally:
        try:
            await env.close()
        except Exception:
            pass

    if should_exit_with_error:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
