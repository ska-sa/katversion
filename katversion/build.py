"""Module that customises setuptools to install __version__ inside package."""

import sys
import os
import warnings
from distutils.command.build import build as DistUtilsBuild
# Ensure we override the correct sdist as setuptools monkey-patches distutils
if "setuptools" in sys.modules:
    from setuptools.command.sdist import log, sdist as OriginalSdist
else:
    from distutils.command.sdist import log, sdist as OriginalSdist

from .version import get_version


def patch_init_py(base_dir, name, version):
    """Patch __init__.py to remove version check and append hard-coded version."""
    # Ensure main package dir is there (may be absent in script-only packages)
    package_dir = os.path.join(base_dir, name)
    if not os.path.isdir(package_dir):
        os.makedirs(package_dir)
    # Open top-level __init__.py and read whole file
    init_py = os.path.join(package_dir, '__init__.py')
    log.info("patching %s to bake in version '%s'" % (init_py, version))
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


class NewStyleDistUtilsBuild(DistUtilsBuild, object):
    """Turn old-style distutils class into new-style one to allow extension."""
    def run(self):
        DistUtilsBuild.run(self)


class AddVersionToInitBuild(NewStyleDistUtilsBuild):
    """Distutils build command that adds __version__ attribute to __init__.py."""
    def run(self):
        # First do normal build (via super, so this can call custom builds too)
        super(NewStyleDistUtilsBuild, self).run()
        # Obtain package name and version (set up via setuptools metadata)
        name = self.distribution.get_name()
        version = self.distribution.get_version()
        # Patch (or create) top-level __init__.py
        patch_init_py(self.build_lib, name, version)


class NewStyleSdist(OriginalSdist, object):
    """Turn old-style distutils class into new-style one to allow extension."""
    def make_release_tree(self, base_dir, files):
        OriginalSdist.make_release_tree(self, base_dir, files)


class AddVersionToInitSdist(NewStyleSdist):
    """Distutils sdist command that adds __version__ attribute to __init__.py."""
    def make_release_tree(self, base_dir, files):
        # First do normal sdist (via super, so this can call custom sdists too)
        super(NewStyleSdist, self).make_release_tree(base_dir, files)
        # Obtain package name and version (set up via setuptools metadata)
        name = self.distribution.get_name()
        version = self.distribution.get_version()
        # Ensure __init__.py is not hard-linked so that we don't change source
        dest = os.path.join(base_dir, name, '__init__.py')
        if hasattr(os, 'link') and os.path.exists(dest):
            os.unlink(dest)
            self.copy_file(os.path.join(name, '__init__.py'), dest)
        # Patch (or create) top-level __init__.py
        patch_init_py(base_dir, name, version)


def setuptools_entry(dist, keyword, value):
    """Setuptools entry point for setting version and adding it to build/sdist."""
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
    class KatVersionBuild(AddVersionToInitBuild, ExistingCustomBuild):
        """First perform existing build and then bake in version string."""
    dist.cmdclass['build'] = KatVersionBuild
    # Extend sdist command to bake version string into source package
    ExistingCustomSdist = dist.cmdclass.get('sdist', object)
    class KatVersionSdist(AddVersionToInitSdist, ExistingCustomSdist):
        """First perform existing sdist and then bake in version string."""
    dist.cmdclass['sdist'] = KatVersionSdist
