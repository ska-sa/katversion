#!/usr/bin/env python

from katversion import setup


setup(name="katversion",
      description="Provides versioning for python packages",
      author="MeerKAT CAM Team",
      author_email="cam@ska.ac.za",
      include_package_data=True,
      scripts=["scripts/kat-get-version.py"],
      url='http://ska.ac.za/',
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: Other/Proprietary License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules"],
      platforms=["OS Independent"],
      keywords="meerkat kat ska",
      tests_require=["unittest2>=0.5.1",
                     "nose>=1.3, <2.0"],
      zip_safe=False,
      test_suite="nose.collector")
