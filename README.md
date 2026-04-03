---
title: Code Review Environment
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
base_path: /docs
models:
  - Qwen/Qwen2.5-7B-Instruct
tags:
  - openenv
  - code-review
  - fastapi
  - python
  - reinforcement-learning
  - meta-pytorch-hackathon
---

# Code Review Environment

### Meta x PyTorch OpenEnv Hackathon — Round 1 Submission

**Built for the Scaler Meta PyTorch Hackathon**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-HuggingFace-orange)](https://prasannakotyal-code-review-env.hf.space) 
[![API Docs](https://img.shields.io/badge/API%20Docs-Swagger-green)](https://prasannakotyal-code-review-env.hf.space/docs)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://docker.com)
[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compatible-red)](https://github.com/meta-pytorch/OpenEnv)

---

## The Problem Statement

The Meta x PyTorch OpenEnv Hackathon challenged participants to:

> **"Build a complete, real-world OpenEnv environment that an AI agent can learn from through the standard step() / reset() / state() API."**

Key requirements:
- Must simulate a real-world task (NOT games or toys)
- Implement full OpenEnv spec with typed models
- Minimum 3 tasks with graders (Easy to Medium to Hard)
- Meaningful reward function with partial progress signals
- Baseline inference script with reproducible scores
- Deploy to Hugging Face Spaces with working Dockerfile

---

## Why Code Review?

Every software company on earth has the same problem — code review is expensive, slow, and depends on senior engineers who are always busy.

Consider these facts:
- A senior engineer spends 3-5 hours per day reviewing code
- Companies like Google, Amazon, and Meta employ thousands of engineers just for reviews
- Junior developers wait days for feedback on their code
- Bugs that slip past review cost companies millions

The solution? Train AI agents to do code review automatically.

Our environment gives AI agents real code snippets and teaches them to find bugs, security vulnerabilities, and quality issues — exactly what a senior engineer does during a pull request review.

This is not a toy problem. This is a skill that has immediate, measurable value in the real world.

---

## What is This Project?

The Code Review Environment is a production-ready Reinforcement Learning environment where AI agents learn to perform intelligent code reviews.

```
AI AGENT
  |
  | obs = env.reset(task_name="style_check")  # Get code to review
  | result = env.step(review_action)          # Submit review
  | print(result.reward)                      # See score (0.0 - 1.0)
  |
  v
CODE REVIEW ENVIRONMENT (Running on Hugging Face)
  |
  | 1. Gives agent a real buggy code snippet
  | 2. Agent reviews it and submits findings
  | 3. Grader scores the review (0.0 - 1.0)
  | 4. Agent receives reward and learns
  |
  v
3 TASK GRADERS
  - style_check:  Style issues (Easy, 5 steps)
  - bug_hunt:     Bug detection (Medium, 7 steps)
  - full_review:   Security + fixes (Hard, 10 steps)
```

---

## The 3 Tasks

### Task 1 — Style Check (Easy)

The agent receives code with style violations and must identify them.

Example:
```python
def calculate(a,b):
    return a+b

result=calculate(10,20)
print(result)
```

What the agent must find:
- Function name should use snake_case (`calculate` → `calculate_sum`)
- Missing spaces around operator (`a+b` → `a + b`)
- Variable should use snake_case (`result` → `result_value`)

**Max steps:** 5 | **Snippets:** 8 | **Reward:** 0.0 - 1.0

---

### Task 2 — Bug Hunt (Medium)

The agent must identify functional bugs and logic errors.

Example (JavaScript):
```javascript
function process(items) {
    let result = [];
    for (let i = 0; i <= items.length; i++) {  // Off-by-one error!
        result.push(items[i] * 2);
    }
    return result;
}
```

What the agent must find:
- Off-by-one error: should use `<` not `<=`
- Accesses undefined on last iteration causing NaN

**Max steps:** 7 | **Snippets:** 8 | **Reward:** 0.0 - 1.0

---

### Task 3 — Full Review (Hard)

The agent must identify security issues AND provide fix suggestions.

Example (Python):
```python
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL Injection!
    cursor.execute(query)
    result = cursor.fetchone()
    conn.close()
    return result
```

What the agent must find:
- SQL injection vulnerability
- No input sanitization on user_id
- No error handling for database operations
- Provide fix: Use parameterized queries

**Max steps:** 10 | **Snippets:** 8 | **Reward:** 0.0 - 1.0

---

## Reward Function

The reward provides partial progress signals — agents don't need to be perfect to learn:

| Component | Weight | Description |
|-----------|--------|-------------|
| Correct issue | 100% | Based on issues correctly identified |
| Fix suggestion | +50% | Bonus for correct fix (hard mode only) |
| False positive | -100% | Penalty for wrong issues |
| Duplicate | 0% | No penalty, no reward |

An agent that finds half the bugs gets rewarded ~0.5. It learns progressively.

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/reset` | POST | Start new episode, get code to review |
| `/step` | POST | Submit review action, get reward |
| `/state` | GET | Get current episode metadata |
| `/docs` | GET | FastAPI OpenAPI documentation |
| `/web` | GET | OpenEnv web playground |

### Try It Online

```bash
# Get a code snippet to review
curl -X POST https://prasannakotyal-code-review-env.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task_name": "style_check"}'

# Submit your review
curl -X POST https://prasannakotyal-code-review-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{"issue_type": "style", "description": "Function name should use snake_case", "line_number": 1}'
```

---

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/prasannakotyal/code_review_env.git
cd code_review_env
uv sync
```

### 2. Run Locally

```bash
uv run python -m server.app
```

Then visit:
- Health: http://127.0.0.1:8000/health
- API Docs: http://127.0.0.1:8000/docs
- Web Playground: http://127.0.0.1:8000/web

### 3. Run Inference

```bash
# Copy and edit environment variables
cp .env.example .env
# Edit .env and add your HF_TOKEN

# Run inference
uv run python inference.py
```

The script outputs the required hackathon format:

```text
[START] task=style_check env=my_env model=Qwen/Qwen2.5-7B-Instruct
[STEP] step=1 action=style@1@Function_name_should_use_snake_case reward=0.33 done=false error=null
[STEP] step=2 action=style@2@Missing_spaces_around_operator reward=0.33 done=false error=null
[END] success=true steps=2 rewards=0.33,0.33
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `HF_TOKEN` | Yes | Hugging Face API token. Get from https://huggingface.co/settings/tokens |
| `API_BASE_URL` | No | LLM endpoint (default: `https://router.huggingface.co/v1`) |
| `MODEL_NAME` | No | Model to use (default: `Qwen/Qwen2.5-7B-Instruct`) |
| `ENV_BASE_URL` | No | Environment URL (default: hosted Space) |
| `MY_ENV_TASK` | No | Task: `style_check`, `bug_hunt`, or `full_review` |
| `TEMPERATURE` | No | LLM temperature (default: 0.0) |
| `MAX_TOKENS` | No | Max tokens per response (default: 300) |

---

## Submission Validation

Before submitting, run these checks:

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests
uv run python -m pytest -q

# Validate OpenEnv spec
uv run openenv validate .

# Build Docker image
docker build -t my-env:latest -f server/Dockerfile .
```

---

## Project Structure

```
my_env/
├── .env.example          # Environment variables template
├── .env.inference        # Default inference config
├── .gitignore
├── Dockerfile            # Container definition (root)
├── LICENSE               # MIT License
├── README.md             # This file
├── __init__.py           # Package exports
├── client.py             # EnvClient for Python
├── inference.py          # Baseline inference script
├── models.py             # Pydantic models
├── openenv.yaml          # OpenEnv metadata
├── pyproject.toml        # Project dependencies
├── requirements.txt      # pip dependencies
├── server/
│   ├── __init__.py
│   ├── app.py            # FastAPI server
│   ├── my_env_environment.py  # Core RL logic
│   ├── Dockerfile        # Server container
│   └── requirements.txt  # Server dependencies
├── scripts/
│   └── validate-submission.sh  # Pre-submission validation
├── tests/
│   ├── test_environment.py
│   └── test_inference.py
└── uv.lock
```

---

## Baseline Scores

| Task | Score | Status |
|------|-------|--------|
| style_check (Easy) | ~0.33 | Passed |
| bug_hunt (Medium) | ~0.50 | Passed |
| full_review (Hard) | ~0.50 | Passed |

---

## Live Links

- **API Docs**: https://prasannakotyal-code-review-env.hf.space/docs
- **Web Playground**: https://prasannakotyal-code-review-env.hf.space/web
- **Health Check**: https://prasannakotyal-code-review-env.hf.space/health
- **Hugging Face Space**: https://huggingface.co/spaces/Prasannakotyal/code-review-env
- **GitHub Repository**: https://github.com/prasannakotyal/code_review_env

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.11 | Core language |
| FastAPI | Web server framework |
| Pydantic | Type-safe data models |
| Docker | Containerization |
| Hugging Face Spaces | Cloud deployment |
| OpenEnv | RL environment framework |
| OpenAI Client | LLM inference |

---

## License

MIT License — See [`LICENSE`](LICENSE)

---

## About

Built for the Meta x PyTorch OpenEnv Hackathon organized by Scaler School of Technology in collaboration with Meta, Hugging Face, and PyTorch.
