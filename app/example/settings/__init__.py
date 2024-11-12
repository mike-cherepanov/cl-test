# ignore F403 here because we need to import all thibs from settings files
from .base import *  # noqa: F403
from .celery import *  # noqa: F403
from .environment import *  # noqa: F403
from .restframework import *  # noqa: F403
