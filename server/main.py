import os

try:
    from openenv.core.env_server.http_server import create_app
except ImportError:
    from openenv.core.env_server import create_app

try:
    from models import CodeReviewAction, CodeReviewObservation
except ImportError:
    from ..models import CodeReviewAction, CodeReviewObservation

from .environment import CodeReviewEnvironment

os.environ.setdefault("ENABLE_WEB_INTERFACE", "true")


app = create_app(
    CodeReviewEnvironment,
    CodeReviewAction,
    CodeReviewObservation,
    env_name="code_review",
)
