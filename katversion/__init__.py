from .version import get_version, build_info
from .build import setup

# Get package version when locally imported from repo or via -e develop install
__version__ = get_version(__path__[0])
