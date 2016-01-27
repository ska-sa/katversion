from .version import get_version, build_info

# BEGIN VERSION CHECK
# Get package version when locally imported from repo or via -e develop install
__version__ = get_version(__path__[0])
# END VERSION CHECK
