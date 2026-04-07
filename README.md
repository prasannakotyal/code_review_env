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

A production-ready OpenEnv environment for code review tasks across Python, JavaScript, and TypeScript.

[![Live API](https://img.shields.io/badge/Live%20API-HuggingFace-orange)](https://prasannakotyal-code-review-env.hf.space)
[![Docs](https://img.shields.io/badge/API%20Docs-Swagger-green)](https://prasannakotyal-code-review-env.hf.space/docs)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://docker.com)
[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compatible-red)](https://github.com/meta-pytorch/OpenEnv)

## Overview

This environment is designed for reinforcement learning agents that perform iterative code review. The agent receives a code snippet and reports issues step-by-step. The environment validates reported issues by type, line range, and semantic description matching.

Current dataset composition:
- 72 curated snippets total
- 24 snippets per task
- 3 languages: Python, JavaScript, TypeScript
- 3 issue classes: style, bug, security

## Tasks

| Task | Difficulty | Max Steps | Snippets | Expected Issue Density |
|------|------------|-----------|----------|-------------------------|
| `style_check` | Easy | 7 | 24 | 1-2 style issues per snippet |
| `bug_hunt` | Medium | 12 | 24 | 2-3 bug issues per snippet |
| `full_review` | Hard | 18 | 24 | 3-4 mixed issues (style + bug + security) |

Hard-mode requirement:
- Every security issue includes a `fix_suggestion`

## Reward Model

Environment step rewards:
- Correct issue: `1.0 / total_issues_in_snippet`
- Incorrect issue: `0.0`
- Duplicate issue: `0.0`
- Hard mode with fix suggestions:
  - Correct issue + good fix: full issue weight
  - Correct issue + missing/weak fix: half issue weight

Final grader score is clamped to `(0.01, 0.99)`.

## Repository Structure

```text
code_review_env/
├── inference.py
├── models.py
├── client.py
├── openenv.yaml
├── server/
│   ├── app.py
│   └── my_env_environment.py
├── tests/
│   ├── test_environment.py
│   ├── test_inference.py
│   └── test_task_requirements.py
├── scripts/
│   └── validate-submission.sh
└── README.md
```

## Quick Start

### 1) Install

```bash
git clone https://github.com/prasannakotyal/code_review_env.git
cd code_review_env
uv sync
```

### 2) Run the server locally

```bash
uv run python -m server.app
```

Open API docs at `http://127.0.0.1:8000/docs`.

### 3) Run baseline inference

Create a local token file (not committed):

```bash
echo "HF_TOKEN=your_token_here" > .env.local
```

Run inference:

```bash
uv run python inference.py
```

Task selection examples:

```bash
MY_ENV_TASK=style_check uv run python inference.py
MY_ENV_TASK=bug_hunt uv run python inference.py
MY_ENV_TASK=full_review uv run python inference.py
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HF_TOKEN` | Yes | - | Hugging Face API token |
| `API_BASE_URL` | No | `https://router.huggingface.co/v1` | LLM API base URL |
| `MODEL_NAME` | No | `Qwen/Qwen2.5-Coder-32B-Instruct` | Model ID |
| `ENV_BASE_URL` | No | hosted HF Space URL | OpenEnv server URL |
| `MY_ENV_TASK` | No | `style_check` | Task name |
| `MY_ENV_BENCHMARK` | No | `my_env` | Benchmark tag |
| `TEMPERATURE` | No | `0.0` | Decoding temperature |
| `MAX_TOKENS` | No | `300` | Max generation tokens |

Security recommendation:
- Store `HF_TOKEN` in `.env.local` (gitignored) or in CI/CD secrets.

## Validation Checklist

Run this sequence before submission:

```bash
uv run pytest tests/ -v
uv run openenv validate
docker build -t code-review-env:latest .
./scripts/validate-submission.sh https://prasannakotyal-code-review-env.hf.space
```

What the script verifies:
- Hosted endpoint responds at `/reset`
- Docker build succeeds
- `openenv validate` passes

## Baseline Results

Measured with `Qwen/Qwen2.5-Coder-32B-Instruct`.

Local updated environment (`ENV_BASE_URL=http://127.0.0.1:8000`):

| Task | Reward | Steps |
|------|--------|-------|
| `style_check` | 0.91 | 3 |
| `bug_hunt` | 0.68 | 3 |
| `full_review` | 0.51 | 3 |

Currently deployed HF Space (before redeploy of latest changes):

| Task | Reward | Steps |
|------|--------|-------|
| `style_check` | 0.99 | 1 |
| `bug_hunt` | 0.99 | 1 |
| `full_review` | 0.99 | 1 |

Target difficulty window after rebalance:
- `style_check`: 0.90-0.95
- `bug_hunt`: 0.60-0.75
- `full_review`: 0.45-0.60

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/reset` | POST | Start episode |
| `/step` | POST | Submit action |
| `/state` | GET | Current state |
| `/docs` | GET | OpenAPI UI |

Example:

```bash
curl -X POST https://prasannakotyal-code-review-env.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task_name": "style_check"}'
```

## Links

- Live API: https://prasannakotyal-code-review-env.hf.space
- API Docs: https://prasannakotyal-code-review-env.hf.space/docs
- Hugging Face Space: https://huggingface.co/spaces/Prasannakotyal/code-review-env
- GitHub: https://github.com/prasannakotyal/code_review_env

## License

MIT - see `LICENSE`.
