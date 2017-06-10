__all__ = ["run"]
from .run import run

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
