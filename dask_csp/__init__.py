from . import config
from .csp.ecs import ECSCluster
from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
