################################################################################
# Copyright (c) 2014-2016, National Research Foundation (Square Kilometre Array)
#
# Licensed under the BSD 3-Clause License (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at
#
#   https://opensource.org/licenses/BSD-3-Clause
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

"""Module that customises setuptools to install __version__ inside package."""

import sys
import os
import warnings
from distutils.command.build_py import build_py as DistUtilsBuildPy
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
        # Append new version attribute to ensure it is authoritative, but only
        # if it is not already there (this happens in pip sdist installs)
        version_cmd = "__version__ = '{0}'\n".format(version)
        if lines[-1] != version_cmd:
            init_file.write("\n# Automatically added by katversion\n")
            init_file.write(version_cmd)
        init_file.truncate()


class NewStyleDistUtilsBuildPy(DistUtilsBuildPy, object):
    """Turn old-style distutils class into new-style one to allow extension."""
    def run(self):
        DistUtilsBuildPy.run(self)


class AddVersionToInitBuildPy(NewStyleDistUtilsBuildPy):
    """Distutils build_py command that adds __version__ attr to __init__.py."""
    def run(self):
        # First do normal build (via super, so this can call custom builds too)
        super(NewStyleDistUtilsBuildPy, self).run()
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
    """Distutils sdist command that adds __version__ attr to __init__.py."""
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
    """Setuptools entry point for setting version and baking it into package."""
    # If 'use_katversion' is False, ignore the rest
    if not value:
        return
    # Enforce the version obtained by katversion, overriding user setting
    version = get_version()
    if dist.metadata.version is not None:
        s = "Ignoring explicit version='{0}' in setup.py, using '{1}' instead"
        warnings.warn(s.format(dist.metadata.version, version))
    dist.metadata.version = version
    # Extend build_py command to bake version string into installed package
    ExistingCustomBuildPy = dist.cmdclass.get('build_py', object)
    class KatVersionBuildPy(AddVersionToInitBuildPy, ExistingCustomBuildPy):
        """First perform existing build_py and then bake in version string."""
    dist.cmdclass['build_py'] = KatVersionBuildPy
    # Extend sdist command to bake version string into source package
    ExistingCustomSdist = dist.cmdclass.get('sdist', object)
    class KatVersionSdist(AddVersionToInitSdist, ExistingCustomSdist):
        """First perform existing sdist and then bake in version string."""
    dist.cmdclass['sdist'] = KatVersionSdist
