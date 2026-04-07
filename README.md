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
  - reinforcement-learning
  - static-analysis
  - python
  - javascript
  - typescript
---

# Code Review Environment

[![Live API](https://img.shields.io/badge/Live%20API-HuggingFace-orange)](https://prasannakotyal-code-review-env.hf.space)
[![API Docs](https://img.shields.io/badge/API%20Docs-Swagger-green)](https://prasannakotyal-code-review-env.hf.space/docs)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://docker.com)
[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compatible-red)](https://github.com/meta-pytorch/OpenEnv)

OpenEnv-compatible reinforcement learning environment for iterative code review across Python, JavaScript, and TypeScript.

## Table of Contents

- [Overview](#overview)
- [Task Definition](#task-definition)
- [Reward and Grading](#reward-and-grading)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API](#api)
- [Validation](#validation)
- [Baseline Measurements](#baseline-measurements)
- [Project Layout](#project-layout)
- [License](#license)

## Overview

The environment presents a code snippet and accepts one issue report per step.
Each report is evaluated against ground truth using issue type, line range, and semantic description matching.

Dataset summary:
- 72 curated snippets total
- 24 snippets per task
- languages: Python, JavaScript, TypeScript
- issue classes: `style`, `bug`, `security`

## Task Definition

| Task | Difficulty | Max Steps | Snippets | Expected Issue Density |
|------|------------|-----------|----------|-------------------------|
| `style_check` | Easy | 7 | 24 | 1-2 style issues per snippet |
| `bug_hunt` | Medium | 12 | 24 | 2-3 bug issues per snippet |
| `full_review` | Hard | 18 | 24 | 3-4 mixed issues per snippet |

Hard task requirements:
- every snippet includes `style` + `bug` + `security`
- every security issue includes `fix_suggestion`

## Reward and Grading

Step reward behavior:
- incorrect issue: `0.0`
- duplicate issue: `0.0`
- correct issue: weighted by `1 / total_issues_in_snippet`
- hard task: fix quality applied on matched security findings

Grader outputs are clamped to `(0.01, 0.99)`.

## Quick Start

### Install

```bash
git clone https://github.com/prasannakotyal/code_review_env.git
cd code_review_env
uv sync
```

### Run server

```bash
uv run python -m server.app
```

Open API docs at `http://127.0.0.1:8000/docs`.

### Run inference

```bash
uv run python inference.py
```

Task-specific runs:

```bash
MY_ENV_TASK=style_check uv run python inference.py
MY_ENV_TASK=bug_hunt uv run python inference.py
MY_ENV_TASK=full_review uv run python inference.py
```

## Configuration

Environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HF_TOKEN` | Yes | - | Hugging Face API token |
| `API_BASE_URL` | No | `https://router.huggingface.co/v1` | LLM API base URL |
| `MODEL_NAME` | No | `Qwen/Qwen2.5-Coder-32B-Instruct` | Model identifier |
| `ENV_BASE_URL` | No | hosted Space URL | OpenEnv server URL |
| `MY_ENV_TASK` | No | `style_check` | Active task |
| `MY_ENV_BENCHMARK` | No | `my_env` | Benchmark tag |
| `TEMPERATURE` | No | `0.0` | Sampling temperature |
| `MAX_TOKENS` | No | `300` | Generation cap |

Credential handling:
- keep `HF_TOKEN` in local environment configuration or CI secret storage
- do not store credentials in source control

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/reset` | POST | Start episode |
| `/step` | POST | Submit action |
| `/state` | GET | Read state |
| `/docs` | GET | OpenAPI docs |

Example:

```bash
curl -X POST https://prasannakotyal-code-review-env.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task_name": "style_check"}'
```

## Validation

Recommended validation sequence:

```bash
uv run pytest tests/ -v
uv run openenv validate
docker build -t code-review-env:latest .
./scripts/validate-submission.sh https://prasannakotyal-code-review-env.hf.space
```

`validate-submission.sh` verifies:
- hosted endpoint availability (`/reset`)
- Docker image build
- OpenEnv compatibility validation

## Baseline Measurements

Model: `Qwen/Qwen2.5-Coder-32B-Instruct`

Current measured baseline:

| Task | Reward | Steps |
|------|--------|-------|
| `style_check` | 0.91 | 3 |
| `bug_hunt` | 0.68 | 3 |
| `full_review` | 0.51 | 3 |

Target calibration window:
- `style_check`: `0.90-0.95`
- `bug_hunt`: `0.60-0.75`
- `full_review`: `0.45-0.60`

## Project Layout

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

## License

MIT - see `LICENSE`.
