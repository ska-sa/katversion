"""Module with functions taking care of proper Python package versioning."""

import os
import time
import re
from subprocess import Popen, PIPE

import pkg_resources  # part of setuptools


VERSION_FILE = '___version___'


def is_git(path=None):
    """Return True if this is a git repo."""
    (repo_dir, stderr) = Popen(['git', 'rev-parse', '--git-dir'], cwd=path,
                               stdout=PIPE, stderr=PIPE).communicate()
    return True if repo_dir else False


def is_svn(path=None):
    """Return True if this is a svn repo."""
    (repo_dir, stderr) = Popen(['svn', 'info'], cwd=path,
                               stdout=PIPE, stderr=PIPE).communicate()
    return True if not stderr else False


def run_cmd(path, *cmd):
    proc = Popen(cmd, cwd=path, stdout=PIPE, stderr=PIPE)
    res, stderr = proc.communicate()
    if stderr:
        raise Exception('###\nCalled process gave error:\n%s\n###' % stderr)
    return res


def normalised(version):
    """Normalise a version string according to PEP 440, if possible."""
    return str(pkg_resources.parse_version(version))


def date_version(scm_type=None):
    """Generate a version string based on the SCM type and the date."""
    dt = str(time.strftime('%Y%m%d%H%M'))
    if scm_type:
        version = "0.0+unknown.{0}.{1}".format(scm_type, dt)
    else:
        version = "0.0+unknown." + dt
    return normalised(version)


def _next_version(version):
    """Turn *version* string into next version by incrementing most minor part."""
    # Allow an arbitrary prefix followed by a traditional dotted version number
    prefix_then_dotted_number = re.compile(r'^(.*?)([\.\d]+)$')
    found = prefix_then_dotted_number.match(version)
    # Give up if the string does not at least end with a number (or dot...)
    if not found:
        return version
    prefix, version_numbers = found.groups()
    version_parts = version_numbers.split('.')
    # Try to increment the last part of dotted version (hopefully it is an int)
    try:
        version_parts[-1] = str(int(version_parts[-1]) + 1)
    except ValueError:
        return version
    else:
        return prefix + '.'.join(version_parts)


def get_git_version(path=None):
    """Get the GIT version."""
    rev_list = run_cmd(path, 'git', 'rev-list', 'HEAD')
    num_commits_since_branch = rev_list.count('\n')

    git_desc = run_cmd(path, 'git', 'describe', '--tags', '--long',
                       '--dirty', '--always')
    git_desc_parts = git_desc.strip().split('-')

    if len(git_desc_parts) == 1:
        git_desc_parts = [0.0, 0, git_desc_parts[0]]
    elif len(git_desc_parts) == 2:
        git_desc_parts = [0.0, 0] + git_desc_parts

    branch_name = run_cmd(path, 'git', 'rev-parse', '--abbrev-ref', 'HEAD')
    branch_name = branch_name.strip().lower()

    release_segment = git_desc_parts[0]
    num_commits_since_tag = git_desc_parts[1]
    short_commit_name = git_desc_parts[2]
    try:
        dirty_check = '.' + git_desc_parts[3]
    except IndexError:
        dirty_check = ''

    # We are at a release if the current commit is tagged and repo is clean
    release = num_commits_since_tag == '0' and not dirty_check

    if release:
        version = "%s" % (release_segment,)
    else:
        # Was: %s.dev%s+%s-%s%s
        # Now: %s.dev%s+%s.%s%s and lower. Still to be normalised.
        version = ("%s.dev%s+%s.%s%s" %
                   (_next_version(release_segment), num_commits_since_branch,
                    branch_name, short_commit_name.lower(), dirty_check))
    return normalised(version)


def get_svn_version(path=None):
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


def get_version_from_module(module=None):
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


def get_version_from_file(path=None):
    """Find the VERSION_FILE and return its contents.

    Returns
    -------
    version: String or None

    """
    # Get version from katversion file.
    if path is None:
        path = os.getcwd()

    version = ''
    filename = os.path.join(path, VERSION_FILE)
    if not os.path.isfile(filename):
        # Look in one directory down.
        filename = os.path.join(os.path.dirname(path), VERSION_FILE)
        if not os.path.isfile(filename):
            filename = ''

    if filename:
        with open(filename) as fh:
            version = fh.readline().strip()
            if version:
                return normalised(version)


def get_version(filename=None, module=None):
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
    filename: None or string, optional
        A file or directory to use to find the SCM checkout path
    module: None or string, optional
        Get version via module name (e.g. __name__ variable)

    Returns
    -------
    version: string
        A string representation of the package version

    """
    # Check the module.
    version = get_version_from_module(module)
    if version:
        return version

    path = ''
    if filename:
        filename = os.path.abspath(filename)
    if filename and os.path.exists(filename):
        if os.path.isdir(filename):
            path = filename
        else:
            path = os.path.dirname(filename)

    if not path or not os.path.isdir(path):
        path = None
    # Check the SCM.
    scm, version = get_version_from_scm(path)
    if version:
        return version

    # Check if there is a katversion file.
    version = get_version_from_file(path)
    if version:
        return version

    # None of the above got a version so we will make one up based on the date.
    return date_version(scm)


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


def get_version_list(filename=None, module=None):
    """Return the version information as a tuple.

    This uses get_version and breaks the string up. Would make more sense if
    the version was a tuple throughout katversion.

    """
    major = 0
    minor = 0
    patch = ''  # PEP440 calls this prerelease, postrelease or devrelease
    ver = get_version(filename, module)
    if ver is not None:
        ver_segments = _sane_version_list(ver.split(".", 2))
        major = ver_segments[0]
        minor = ver_segments[1]
        patch = ".".join(ver_segments[2:])  # Rejoin the .

    # Return None as first field, makes substitution easier in next step.
    return [None, major, minor, patch]


def build_info(name, filename=None, module=None):
    """Return the build info tuple."""
    verlist = get_version_list(filename=filename, module=module)
    verlist[0] = name
    return tuple(verlist)
