"""Module with functions taking care of proper python package versioning."""

import os
import time

from subprocess import Popen, PIPE
import pkg_resources  # part of setuptools


VERSION_FILE = '___version___'


def is_git(path=None):
    """Return true if this is a git repo."""
    (repo_dir, stderr) = Popen(['git', 'rev-parse', '--git-dir'], cwd=path,
                               stdout=PIPE, stderr=PIPE).communicate()
    return True if repo_dir else False


def is_svn(path=None):
    """Return true if this is a svn repo."""
    (repo_dir, stderr) = Popen(['svn', 'info'], cwd=path,
                               stdout=PIPE, stderr=PIPE).communicate()
    return True if not stderr else False


def check_for_error(err):
    if err:
        raise Exception('###\nCalled process gave error:\n%s\n###' % err)


def get_git_version(release=False, path=None):
    """Get the GIT version."""
    (rev_list, stderr) = Popen(['git', 'rev-list', 'HEAD'], cwd=path,
                               stdout=PIPE, stderr=PIPE).communicate()
    check_for_error(stderr)
    num_commits_since_branch = rev_list.count('\n')

    (git_desc, stderr) = Popen(['git', 'describe', '--tags', '--long',
                                '--dirty', '--always'], cwd=path,
                               stdout=PIPE, stderr=PIPE).communicate()
    check_for_error(stderr)
    git_desc_parts = git_desc.strip().split('-')

    if len(git_desc_parts) == 1:
        git_desc_parts = [0.0, 0, git_desc_parts[0]]
    elif len(git_desc_parts) == 2:
        git_desc_parts = [0.0, 0] + git_desc_parts

    (branch_name, stderr) = Popen(['git', 'rev-parse',
                                   '--abbrev-ref', 'HEAD'], cwd=path,
                                  stdout=PIPE, stderr=PIPE).communicate()
    check_for_error(stderr)
    branch_name = branch_name.strip()

    release_segment = git_desc_parts[0]
    # num_commits_since_tag = git_desc_parts[1]  # We ignore this value
    short_commit_name = git_desc_parts[2]

    try:
        dirty_check = '-' + git_desc_parts[3]
    except IndexError:
        dirty_check = ''

    if release:
        version = "%s" % (release_segment,)
    else:
        # Was: %s.dev%s+%s-%s%s
        # Now: %s.dev%s+%s.%s%s and lower. Skip the normalisation done by pip.
        version = ("%s.dev%s+%s.%s%s" %
                   (release_segment, num_commits_since_branch, branch_name,
                    short_commit_name.lower(), dirty_check))
    return version


def get_svn_version(release=False, path=None):
    """Return the version string from svn."""
    # Unimplemented, there is probably code to do this already for SVN
    # if you know where that is place it here please.
    return date_version('svn')


def date_version(scm_type=None):
    """Generate a version string based on the SCM type and the date."""
    dt = str(time.strftime('%Y%m%d%H%M'))
    if scm_type:
        version = "0.0+unknown.{0}-{1}".format(scm_type, dt)
    else:
        version = "0.0+unknown." + dt
    return version


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
                return version


def get_version_from_scm(release=False, path=None):
    """Get the current version string of this package using git.

    This function ensures that the version string complies with PEP440.
    The format of our version string is:

        - for RELEASE builds:
            <major>.<minor>
          e.g.
            0.1
            2.4

        - for DEVELOPMENT builds:
            <major>.<minor>.dev<num_branch_commits> \
            +<branch_name>-<short_git_sha>[-dirty]
          e.g.
            1.1.dev34+new_shiny_feature-efa973da
            0.1.dev7+master-gb91ffa6-dirty

    Parameters
    ----------
    release : boolean
        Whether this version is for a formal RELEASE build or
        not (default=False)

    Returns
    -------
    version : boolean
        The version string for this package

    """
    if is_git(path):
        return 'git', get_git_version(release, path)
    elif is_svn(path):
        return 'svn', get_svn_version(release, path)
    return None, None


def get_version_from_module(module=None):
    if module is not None:
        # Setup.py will not pass in a module, but creating __version__ from
        # __init__ will.
        module = str(module).split('.', 1)[0]
        try:
            return pkg_resources.require(module)[0].version
        except pkg_resources.DistributionNotFound:
            # So there you have it the module is not installed.
            pass


def get_version(filename=None, release=False, module=None):
    """Return the version string.

    Parameters
    ----------

    filename: Optional String
        A file or directory to use to find the SCM checkout path.
    release: Optional Boolean
        True return a short release version and not the pre-relase version.
    module: Optional String
        Usually pass in __name__, the module name.

    Returns
    -------

    version: String
        A string representation of the package version.

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
    scm, version = get_version_from_scm(release, path)
    if version:
        return version

    # Check if there is a katversion file.
    version = get_version_from_file(path)
    if version:
        return version

    # None of the above got a version so we will make one up based on the date.
    return date_version(scm)
