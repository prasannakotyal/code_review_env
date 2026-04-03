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
---

# Code Review Environment

An OpenEnv-compatible code review benchmark built for the Scaler Meta PyTorch Hackathon. The environment evaluates agents on realistic review tasks across style, correctness, and security, and is packaged for local development, Docker deployment, Hugging Face Spaces hosting, and hosted inference through the Hugging Face router.

## Submission Assets

| Asset | Link |
| --- | --- |
| GitHub repository | https://github.com/prasannakotyal/code_review_env |
| Hugging Face Space | https://huggingface.co/spaces/Prasannakotyal/code-review-env |
| Hosted API | https://prasannakotyal-code-review-env.hf.space |
| Hosted API docs | https://prasannakotyal-code-review-env.hf.space/docs |
| Hosted web playground | https://prasannakotyal-code-review-env.hf.space/web |
| Default inference model | https://huggingface.co/Qwen/Qwen2.5-7B-Instruct |

## Benchmark Overview

This repository exposes a single OpenEnv environment named `code_review`. Each episode presents one code snippet and asks the agent to identify real issues with the correct line number, description, and, for the hardest task, an appropriate fix suggestion.

### Task Inventory

| Task | Focus | Difficulty | Max steps | Snippets |
| --- | --- | --- | --- | --- |
| `style_check` | Naming, formatting, and conventions | Easy | 5 | 8 |
| `bug_hunt` | Functional and logic issues | Medium | 7 | 8 |
| `full_review` | Security and correctness, with fix suggestions | Hard | 10 | 8 |

### Coverage

- Total snippets: 24
- Languages: 15 Python, 6 JavaScript, 3 TypeScript
- Reward range: normalized to `0.00` through `1.00`
- Duplicate reports and false positives: `0.00`

## API Surface

| Endpoint | Purpose |
| --- | --- |
| `POST /reset` | Start a new episode and receive a code snippet |
| `POST /step` | Submit a review action and receive reward, updated observation, and done flag |
| `GET /state` | Inspect the current environment state |
| `GET /health` | Liveness check |
| `GET /docs` | FastAPI OpenAPI documentation |
| `GET /web` | OpenEnv web playground |

### Example

```bash
curl -X POST https://prasannakotyal-code-review-env.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task_name":"style_check"}'
```

## Local Development

For normal local use, install only the runtime environment:

```bash
uv sync
uv run python -m server.app
```

Then verify the environment locally:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/docs
curl http://127.0.0.1:8000/web
```

## Hosted Inference

The repository includes `.env.example` and `.env.inference` for baseline inference configuration. The default hosted setup uses:

- `API_BASE_URL=https://router.huggingface.co/v1`
- `MODEL_NAME=Qwen/Qwen2.5-7B-Instruct`
- `ENV_BASE_URL=https://prasannakotyal-code-review-env.hf.space`

`inference.py` loads configuration from environment variables and local env files, and resolves credentials in this order:

1. `HF_TOKEN`
2. `API_KEY` or `OPENAI_API_KEY`
3. `~/.cache/huggingface/token`
4. `~/.cache/hugging_face/token`

Run the baseline inference script with:

```bash
uv run python inference.py
```

The script uses the OpenAI client and emits the required hackathon logging contract:

```text
[START] task=<task_name> env=<benchmark> model=<model_name>
[STEP] step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
[END] success=<true|false> steps=<n> rewards=<r1,r2,...,rn>
```

## Submission Validation

For the pre-submission checks below, install the development dependency set once. The `dev` extra is only for local validation tooling such as `pytest`.

```bash
uv sync --extra dev
```

Then run the submission checks:

```bash
uv run python -m pytest -q
uv run python -m compileall .
uv run openenv validate . --json
docker build -t code-review-env .
./scripts/validate-submission.sh https://prasannakotyal-code-review-env.hf.space .
```

### Latest Verification

The repository has been checked end to end with the current hosted Space:

- `uv run python -m pytest -q` - passed
- `uv run openenv validate . --json` - passed
- `docker build -t code-review-env` - passed
- `./scripts/validate-submission.sh https://prasannakotyal-code-review-env.hf.space .` - passed
- `uv run python inference.py` - passed against the hosted Space with `success=true`

## Repository Layout

```text
code_review_env/
├── .dockerignore
├── .env.example
├── .env.inference
├── Dockerfile
├── LICENSE
├── README.md
├── client.py
├── inference.py
├── models.py
├── openenv.yaml
├── pyproject.toml
├── requirements.txt
├── scripts/
│   └── validate-submission.sh
├── server/
│   ├── app.py
│   ├── environment.py
│   └── main.py
└── tests/
```

## License

Released under the MIT License. See [`LICENSE`](LICENSE).
