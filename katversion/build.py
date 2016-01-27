"""Module that customises setuptools to install __version__ inside package."""

import os
from distutils.command.build import build as DistUtilsBuild
import warnings

from .version import get_version


class NewStyleDistUtilsBuild(DistUtilsBuild, object):
    """Turn old-style distutils class into new-style one."""
    def run(self):
        DistUtilsBuild.run(self)


class AddVersionToInitBuild(NewStyleDistUtilsBuild):
    """Distutils build command that adds __version__ attribute to __init__.py."""
    def run(self):
        # First run the normal build procedure
        super(NewStyleDistUtilsBuild, self).run()
        # Obtain package name and version (set up via setuptools metadata)
        name = self.distribution.get_name()
        version = self.distribution.get_version()
        # Ensure lib build dir is there (may be absent in script-only packages)
        module_build_dir = os.path.join(self.build_lib, name)
        if not os.path.isdir(module_build_dir):
            os.makedirs(module_build_dir)
        # Open top-level __init__.py and read whole file
        init_py = os.path.join(module_build_dir, "__init__.py")
        with open(init_py, 'r+') as init_file:
            lines = init_file.readlines()
            # Search for sentinels indicating version checking block
            try:
                begin = lines.index("# BEGIN VERSION CHECK\n")
                end = lines.index("# END VERSION CHECK\n")
            except ValueError:
                begin = end = len(lines)
            # Delete existing repo version checking block in file
            init_file.seek(0)
            init_file.writelines(lines[:begin] + lines[end+1:])
            # Append new version attribute to ensure it is authoritative
            init_file.write("\n# Automatically added by katversion\n")
            init_file.write("__version__ = '{0}'\n".format(version))
            init_file.truncate()


def setuptools_entry(dist, keyword, value):
    """Setuptools entry point for setting version and adding it to build."""
    # If 'use_katversion' is False, ignore the rest
    if not value:
        return
    # Enforce the version obtained by katversion, overriding user setting
    version = get_version()
    if dist.metadata.version is not None:
        s = "Ignoring explicit version='{0}' in setup.py, using '{1}' instead"
        warnings.warn(s.format(dist.metadata.version, version))
    dist.metadata.version = version
    # Extend build command to bake version string into installed package
    ExistingCustomBuild = dist.cmdclass.get('build', object)
    class FullVersionedBuild(AddVersionToInitBuild, ExistingCustomBuild):
        """First perform existing build and then bake in version string."""
    dist.cmdclass['build'] = FullVersionedBuild
