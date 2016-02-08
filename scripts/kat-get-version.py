#!/usr/bin/env python
"""Script to get the current version string of a Python package."""

import os
import argparse

from katversion import get_version


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', dest='path', action='store',
                        help='Path of SCM checkout. If not given the'
                             ' current directory is used.')
    args = parser.parse_args()

    if args.path:
        path = args.path
    else:
        # If path was not given us the current working directory. This is the
        # way git smudge uses this file.
        path = os.getcwd()
    print get_version(path)
