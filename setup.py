#!/usr/bin/env python

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

from setuptools import dist, setup, find_packages

# Ensure we have pkginfo before we start as it is needed before we call setup()
# If not installed system-wide it will be downloaded into the local .eggs dir
dist.Distribution(dict(setup_requires='pkginfo'))

# These are safe to import inside setup.py as the only external dependencies
# are setuptools and pkginfo and they are both now available
from katversion import get_version
from katversion.build import AddVersionToInitBuildPy, AddVersionToInitSdist


with open('README.rst') as readme:
    long_description = readme.read()

setup(name="katversion",
      description="Reliable git-based versioning for Python packages",
      long_description=long_description,
      author="The MeerKAT CAM Team",
      author_email="cam@ska.ac.za",
      packages=find_packages(),
      include_package_data=True,
      scripts=["scripts/kat-get-version.py"],
      url='https://github.com/ska-sa/katversion',
      license="BSD",
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Topic :: Software Development :: Version Control",
          "Topic :: System :: Software Distribution",
          "Topic :: Software Development :: Libraries :: Python Modules"],
      platforms=["OS Independent"],
      keywords="versioning meerkat ska",
      # Register 'use_katversion' keyword for use in participating setup.py files
      entry_points={'distutils.setup_keywords':
                    'use_katversion = katversion.build:setuptools_entry'},
      # Handle our own version directly instead of via entry point
      version=get_version(),
      cmdclass={'build_py': AddVersionToInitBuildPy,
                'sdist': AddVersionToInitSdist},
      # We need pkginfo to get our own version (it will already be there
      # so this is more for documentation purposes)
      setup_requires=['pkginfo'],
      # We also need pkginfo to get the versions of other packages
      install_requires=['pkginfo'],
      tests_require=["unittest2>=0.5.1",
                     "nose>=1.3, <2.0"],
      zip_safe=False,
      test_suite="nose.collector")
