import asyncio
import os

from client import CodeReviewEnv
from models import CodeReviewAction, IssueType


ENV_BASE_URL = os.getenv(
    "ENV_BASE_URL", "https://prasannakotyal-code-review-env.hf.space"
)


async def main() -> None:
    env = CodeReviewEnv(base_url=ENV_BASE_URL)

    async with env:
        result = await env.reset(task_name="style_check")
        obs = result.observation

        print("\nRESET")
        print("=" * 60)
        print(obs.message)
        print(f"language={obs.language.value} remaining={obs.issues_remaining}")
        print("\nCODE\n")
        print(obs.code_snippet)

        actions = [
            CodeReviewAction(
                issue_type=IssueType.STYLE,
                description="Function name should use snake_case",
                line_number=1,
            ),
            CodeReviewAction(
                issue_type=IssueType.STYLE,
                description="Missing spaces around operator",
                line_number=2,
            ),
            CodeReviewAction(
                issue_type=IssueType.STYLE,
                description="Variable should use snake_case",
                line_number=4,
            ),
        ]

        for idx, action in enumerate(actions, 1):
            result = await env.step(action)
            obs = result.observation

            print(f"\nSTEP {idx}")
            print("=" * 60)
            print(
                f"action={action.issue_type.value} "
                f"line={action.line_number} "
                f"desc={action.description}"
            )
            print(f"reward={result.reward} done={result.done}")
            print(obs.message)
            print(f"remaining={obs.issues_remaining}")
            print(f"found={len(obs.issues_found)}")

            if result.done:
                break


if __name__ == "__main__":
    asyncio.run(main())
