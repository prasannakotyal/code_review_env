try:
    from openenv.core.env_server.http_server import create_app
except ImportError:
    from openenv.core.env_server import create_app

try:
    from models import CodeReviewAction, CodeReviewObservation
except ImportError:
    from ..models import CodeReviewAction, CodeReviewObservation

from .my_env_environment import MyEnvironment

import os

os.environ.setdefault("ENABLE_WEB_INTERFACE", "true")


app = create_app(
    MyEnvironment,
    CodeReviewAction,
    CodeReviewObservation,
    env_name="my_env",
    max_concurrent_envs=4,
)


def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
