"""Module that customises setuptools to install __version__ inside package."""

import os
from distutils.command.build import build as DistUtilsBuild
import warnings

from setuptools import setup as _setup
from setuptools import find_packages

from .version import get_version


class AddVersionToInitBuild(DistUtilsBuild):
    """Distutils build command that adds __version__ attribute to __init__.py."""
    def run(self):
        # First run the normal build procedure
        DistUtilsBuild.run(self)
        # Obtain package name and version (set up via setuptools metadata)
        name = self.distribution.get_name()
        version = self.distribution.get_version()
        # Ensure lib build dir is there (may be absent in script-only packages)
        module_build_dir = os.path.join(self.build_lib, name)
        if not os.path.isdir(module_build_dir):
            os.makedirs(module_build_dir)
        # Get top-level __init__.py
        init_py = os.path.join(module_build_dir, "__init__.py")
        # Append version command to file (create if not there)
        with open(init_py, 'a') as init_file:
            init_file.write("\n# Automatically added by katversion\n")
            init_file.write("__version__ = '{0}'\n".format(version))


def setup(**kwargs):
    """Enhanced setuptools.setup that fixes version and does find_packages."""
    # Enforce the version obtained by katversion, overriding user setting
    version = get_version()
    if 'version' in kwargs:
        s = "Ignoring explicit version='{0}' in setup.py, using '{1}' instead"
        warnings.warn(s.format(kwargs['version'], version))
    kwargs['version'] = version
    # Do standard thing to get packages if not specified
    kwargs['packages'] = kwargs.get('packages', find_packages())
    # Override build command
    kwargs['cmdclass'] = {'build': AddVersionToInitBuild}
    # Now continue with the usual setup
    return _setup(**kwargs)
