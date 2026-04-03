---
title: Code Review Environment
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
base_path: /docs
models:
  - Qwen/Qwen2.5-Coder-32B-Instruct
tags:
  - openenv
  - code-review
  - fastapi
  - python
  - reinforcement-learning
  - meta-pytorch-hackathon
---

# Code Review Environment

### Meta x PyTorch OpenEnv Hackathon - Round 1 Submission

**Built for the Scaler Meta PyTorch Hackathon**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-HuggingFace-orange)](https://prasannakotyal-code-review-env.hf.space) 
[![API Docs](https://img.shields.io/badge/API%20Docs-Swagger-green)](https://prasannakotyal-code-review-env.hf.space/docs)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://docker.com)
[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compatible-red)](https://github.com/meta-pytorch/OpenEnv)

---

## Overview

The Code Review Environment is a production-ready Reinforcement Learning environment where AI agents learn to perform intelligent code reviews. It contains **225 real-world code snippets** across 3 languages (Python, JavaScript, TypeScript) with issues in 3 categories (style, bugs, security).

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
  - full_review:  Security + fixes (Hard, 10 steps)
```

---

## The 3 Tasks

| Task | Difficulty | Max Steps | Snippets | Focus |
|------|------------|-----------|----------|-------|
| `style_check` | Easy | 5 | 75 | Style violations, naming, formatting |
| `bug_hunt` | Medium | 7 | 75 | Logic errors, runtime bugs, edge cases |
| `full_review` | Hard | 10 | 75 | Security vulnerabilities + fix suggestions |

### Task 1: Style Check (Easy)

Find style violations like naming conventions, missing type hints, and formatting issues.

```python
# Example snippet
def calculate(a,b):
    return a+b
result=calculate(10,20)
```

Issues to find: f-string usage, list comprehension, snake_case naming, type hints

### Task 2: Bug Hunt (Medium)

Find functional bugs like off-by-one errors, null checks, and logic issues.

```javascript
// Example snippet
function process(items) {
    for (let i = 0; i <= items.length; i++) {  // Off-by-one!
        result.push(items[i] * 2);
    }
}
```

Issues to find: array bounds, null/undefined, async/await, type mismatches

### Task 3: Full Review (Hard)

Find security vulnerabilities AND provide fix suggestions.

```python
# Example snippet
query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL Injection!
cursor.execute(query)
```

Issues to find: SQL injection, XSS, hardcoded secrets, path traversal

---

## Reward Function

| Action | Reward |
|--------|--------|
| Correct issue found | `1.0 / total_issues` |
| Correct issue + fix (hard mode) | Full weight |
| Correct issue, wrong fix (hard mode) | Half weight |
| Wrong issue (false positive) | 0.0 |
| Duplicate issue | 0.0 |

Total reward is normalized to 0.0 - 1.0 range.

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

Visit: http://127.0.0.1:8000/docs

### 3. Run Inference

```bash
# Create local env file with your token (never committed)
echo "HF_TOKEN=your_token_here" > .env.local

# Run inference
uv run python inference.py
```

Output format:
```
[START] task=style_check env=my_env model=Qwen/Qwen2.5-Coder-32B-Instruct
[STEP] step=1 action=style@2@Use_arrow_function reward=1.00 done=true error=null
[END] success=true steps=1 rewards=1.00
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HF_TOKEN` | Yes | - | HuggingFace API token |
| `API_BASE_URL` | No | `https://router.huggingface.co/v1` | LLM endpoint |
| `MODEL_NAME` | No | `Qwen/Qwen2.5-Coder-32B-Instruct` | Model to use |
| `ENV_BASE_URL` | No | HF Space URL | Environment URL |
| `MY_ENV_TASK` | No | `style_check` | Task name |

**Security Note:** Store your `HF_TOKEN` in `.env.local` (gitignored) or as a GitHub Secret for CI/CD.

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/reset` | POST | Start new episode |
| `/step` | POST | Submit review action |
| `/state` | GET | Get current state |
| `/docs` | GET | OpenAPI documentation |

### Example API Call

```bash
# Reset and get code snippet
curl -X POST https://prasannakotyal-code-review-env.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task_name": "style_check"}'

# Submit review
curl -X POST https://prasannakotyal-code-review-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{"issue_type": "style", "description": "Use arrow function", "line_number": 2}'
```

---

## Validation

```bash
# Run tests
uv run pytest tests/ -v

# Validate OpenEnv spec
uv run openenv validate

# Build Docker
docker build -t code-review-env:latest .

# Full validation
./scripts/validate-submission.sh https://prasannakotyal-code-review-env.hf.space
```

---

## Project Structure

```
code_review_env/
├── inference.py              # Baseline inference script
├── models.py                 # Pydantic models (Action, Observation)
├── client.py                 # Python client for environment
├── openenv.yaml              # OpenEnv specification
├── server/
│   ├── app.py                # FastAPI server
│   └── my_env_environment.py # Core environment (225 snippets)
├── tests/
│   ├── test_environment.py
│   └── test_inference.py
├── scripts/
│   └── validate-submission.sh
├── .env.inference            # Default config (no secrets)
├── .gitignore                # Ignores .env.local, secrets
├── Dockerfile
└── README.md
```

---

## Baseline Scores

| Task | Model | Reward | Steps |
|------|-------|--------|-------|
| style_check | Qwen2.5-Coder-32B | 1.00 | 1 |
| bug_hunt | Qwen2.5-Coder-32B | 1.00 | 1 |
| full_review | Qwen2.5-Coder-32B | 1.00 | 1 |

---

## Team Setup

For teammates:

1. Clone the repo: `git clone git@github.com:prasannakotyal/code_review_env.git`
2. Create your own `.env.local` with your HF token
3. Run `uv sync` to install dependencies
4. Run tests: `uv run pytest`

**Note:** Each team member uses their own HF token in `.env.local`. The file is gitignored and never shared.

---

## Links

- **Live API**: https://prasannakotyal-code-review-env.hf.space
- **API Docs**: https://prasannakotyal-code-review-env.hf.space/docs
- **HF Space**: https://huggingface.co/spaces/Prasannakotyal/code-review-env
- **GitHub**: https://github.com/prasannakotyal/code_review_env

---

## License

MIT License - See [LICENSE](LICENSE)

---

Built for the Meta x PyTorch OpenEnv Hackathon organized by Scaler School of Technology.
