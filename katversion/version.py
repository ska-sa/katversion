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

"""Module with functions taking care of proper Python package versioning."""

import os
import time
import re
from subprocess import Popen, PIPE

import pkg_resources  # part of setuptools
try:
    # This requires setuptools >= 12
    from pkg_resources import parse_version, SetuptoolsVersion
except ImportError:
    parse_version = SetuptoolsVersion = None
from pkginfo import UnpackedSDist


VERSION_FILE = '___version___'


def run_cmd(path, *cmd):
    proc = Popen(cmd, cwd=path, stdout=PIPE, stderr=PIPE,
                 universal_newlines=True)
    res, stderr = proc.communicate()
    if stderr:
        raise RuntimeError('###\nCalled process gave error:\n%s\n###' % stderr)
    return res


def is_git(path):
    """Return True if this is a git repo."""
    try:
        repo_dir = run_cmd(path, 'git', 'rev-parse', '--git-dir')
        return True if repo_dir else False
    except (OSError, RuntimeError):
        return False


def is_svn(path):
    """Return True if this is an svn repo."""
    try:
        repo_dir = run_cmd(path, 'svn', 'info')
        return True
    except (OSError, RuntimeError):
        return False


def date_version(scm=None):
    """Generate a version string based on the SCM type and the date."""
    dt = str(time.strftime('%Y%m%d%H%M'))
    if scm:
        version = "0.0+unknown.{0}.{1}".format(scm, dt)
    else:
        version = "0.0+unknown." + dt
    return version


def get_git_version(path):
    """Get the GIT version."""
    # Get name of current branch (or 'HEAD' for a detached HEAD)
    branch_name = run_cmd(path, 'git', 'rev-parse', '--abbrev-ref', 'HEAD')
    branch_name = branch_name.strip()
    # Determine whether working copy is dirty (i.e. contains modified files)
    mods = run_cmd(path, 'git', 'status', '--porcelain', '--untracked-files=no')
    dirty = '.dirty' if mods else ''
    # Get a list of all commits on branch, with corresponding branch/tag refs
    # Each line looks something like: "d3e4d42 (HEAD, master, tag: v0.1)"
    git_output = run_cmd(path, 'git', 'log', '--pretty="%h%d"')
    commits = git_output.strip().replace('"', '').split('\n')
    num_commits_since_branch = len(commits)
    # Short hash of the latest commit
    short_commit_name = commits[0].partition(' ')[0]
    # A valid version is a sequence of dotted numbers optionally prefixed by 'v'
    valid_version = re.compile(r'^v?([\.\d]+)$')
    def tagged_version(commit):
        """First tag on commit that is valid version, as a list of numbers."""
        refs = commit.partition(' ')[2]
        for ref in refs.lstrip('(').rstrip(')').split(', '):
            if ref.startswith('tag: '):
                tag = ref[5:].lower()
                found = valid_version.match(tag)
                if found:
                    return [int(v) for v in found.group(1).split('.') if v]
        return []
    # Walk back along branch and find first valid tagged version (or use 0.0)
    for commit in commits:
        version_numbers = tagged_version(commit)
        if version_numbers:
            break
    else:
        version_numbers = [0, 0]
    # It is a release if the current commit has a version tag (and dir is clean)
    release = (commit == commits[0]) and not dirty
    if not release:
        # We are working towards the next (minor) release according to PEP 440
        version_numbers[-1] += 1
    version = '.'.join([str(v) for v in version_numbers])
    if not release:
        # Development version contains extra embellishments
        version = ("%s.dev%d+%s.%s%s" % (version, num_commits_since_branch,
                                         branch_name, short_commit_name, dirty))
    return version


def get_svn_version(path):
    """Return the version string from svn."""
    # Unimplemented, there is probably code to do this already for SVN
    # if you know where that is place it here please.
    return date_version('svn')


def get_version_from_scm(path=None):
    """Get the current version string of this package using SCM tool.

    Parameters
    ----------
    path : None or string, optional
        The SCM checkout path (default is current directory)

    Returns
    -------
    version : string
        The version string for this package

    """
    if is_git(path):
        return 'git', get_git_version(path)
    elif is_svn(path):
        return 'svn', get_svn_version(path)
    return None, None


def get_version_from_module(module):
    """Use pkg_resources to get version of installed module by name."""
    if module is not None:
        # Setup.py will not pass in a module, but creating __version__ from
        # __init__ will.
        module = str(module).split('.', 1)[0]
        try:
            package = pkg_resources.get_distribution(module)
            return package.version
        except pkg_resources.DistributionNotFound:
            # So there you have it the module is not installed.
            pass


def get_version_from_unpacked_sdist(path):
    """Assume path points to an unpacked source distribution and get version."""
    try:
        return UnpackedSDist(path).version
    except ValueError:
        # Could not load path as an unpacked sdist
        pass


def get_version_from_file(path):
    """Find the VERSION_FILE and return its contents.

    Returns
    -------
    version : string or None

    """
    filename = os.path.join(path, VERSION_FILE)
    if not os.path.isfile(filename):
        # Look in the parent directory of path instead.
        filename = os.path.join(os.path.dirname(path), VERSION_FILE)
        if not os.path.isfile(filename):
            filename = ''

    if filename:
        with open(filename) as fh:
            version = fh.readline().strip()
            if version:
                return version


def normalised(version):
    """Normalise a version string according to PEP 440, if possible."""
    if parse_version:
        # Let setuptools (>= 12) do the normalisation
        return str(parse_version(version))
    else:
        # Homegrown normalisation for older setuptools (< 12)
        public, sep, local = version.lower().partition('+')
        # Remove leading 'v' from public version
        if len(public) >= 2:
            if public[0] == 'v' and public[1] in '0123456789':
                public = public[1:]
        # Turn all characters except alphanumerics into periods in local version
        alphanum_or_period = ['.'] * 256
        for c in 'abcdefghijklmnopqrstuvwxyz0123456789':
            alphanum_or_period[ord(c)] = c
        local = local.translate(''.join(alphanum_or_period))
        return public + sep + local


def get_version(path=None, module=None):
    """Return the version string.

    This function ensures that the version string complies with PEP 440.
    The format of our version string is:

        - for RELEASE builds:
            <major>.<minor>
          e.g.
            0.1
            2.4

        - for DEVELOPMENT builds:
            <major>.<minor>.dev<num_branch_commits> \
            +<branch_name>.g<short_git_sha>[.dirty]
          e.g.
            1.1.dev34+new.shiny.feature.gfa973da
            0.1.dev7+master.gb91ffa6.dirty

        - for UNKNOWN builds:
            0.0+unknown.[<scm_type>.]<date>
          e.g.
            0.0+unknown.svn.201402031023
            0.0+unknown.201602081715

    The <major>.<minor> substring for development builds will be that of the
    NEXT (minor) release, in order to allow proper Python version ordering.

    Parameters
    ----------
    path : None or string, optional
        A file or directory to use to find the SCM or sdist checkout path
        (default is the current working directory)
    module : None or string, optional
        Get version via module name (e.g. __name__ variable), which takes
        precedence over path if provided (ignore otherwise)

    Returns
    -------
    version: string
        A string representation of the package version

    """
    # Check the module option first.
    version = get_version_from_module(module)
    if version:
        return normalised(version)

    # Turn path into a valid directory (default is current directory)
    if path is None:
        path = os.getcwd()
    path = os.path.abspath(path)
    if os.path.exists(path) and not os.path.isdir(path):
        path = os.path.dirname(path)
    if not os.path.isdir(path):
        raise ValueError('No such package source directory: %r' % (path,))

    # Check for an sdist in the process of being installed by pip.
    version = get_version_from_unpacked_sdist(path)
    if version:
        return normalised(version)

    # Check the SCM.
    scm, version = get_version_from_scm(path)
    if version:
        return normalised(version)

    # Check if there is a katversion file in the given path.
    version = get_version_from_file(path)
    if version:
        return normalised(version)

    # None of the above got a version so we will make one up based on the date.
    return normalised(date_version(scm))


def _sane_version_list(version):
    """Ensure the major and minor are int.

    Parameters
    ----------
    version: list
        Version components

    Returns
    -------
    version: list
        List of components where first two components has been sanitised

    """
    v0 = str(version[0])
    if v0:
        # Test if the major is a number.
        try:
            v0 = v0.lstrip("v").lstrip("V")
            # Handle the common case where tags have v before major.
            v0 = int(v0)
        except ValueError:
            v0 = None

    if v0 is None:
        version = [0, 0] + version
    else:
        version[0] = v0

    try:
        # Test if the minor is a number.
        version[1] = int(version[1])
    except ValueError:
        # Insert Minor 0.
        version = [version[0], 0] + version[1:]

    return version


def get_version_list(path=None, module=None):
    """Return the version information as a tuple.

    This uses get_version and breaks the string up. Would make more sense if
    the version was a tuple throughout katversion.

    """
    major = 0
    minor = 0
    patch = ''  # PEP440 calls this prerelease, postrelease or devrelease
    ver = get_version(path, module)
    if ver is not None:
        ver_segments = _sane_version_list(ver.split(".", 2))
        major = ver_segments[0]
        minor = ver_segments[1]
        patch = ".".join(ver_segments[2:])  # Rejoin the .

    # Return None as first field, makes substitution easier in next step.
    return [None, major, minor, patch]


def build_info(name, path=None, module=None):
    """Return the build info tuple."""
    verlist = get_version_list(path, module)
    verlist[0] = name
    return tuple(verlist)
