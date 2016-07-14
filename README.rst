katversion
==========

The *katversion* package provides proper versioning for Python packages as
dictated by their (git) source repositories. The resulting version string is
baked into the installed package's ``__init__.py`` file for guaranteed
traceability when imported (no dependency on what pkg_resources thinks!).

Version String Format
---------------------

*katversion* generates a version string for your SCM package that
complies with `PEP 440 <https://www.python.org/dev/peps/pep-0440/>`_.
It mainly supports git repositories, with a half-hearted attempt at svn support.

The format of our version string is:

::

    - for RELEASE builds:
        <major>.<minor>
        e.g.
        0.1
        2.4

    - for DEVELOPMENT builds:
        <major>.<minor>.dev<num_commits>+<branch_name>.g<short_git_sha>[.dirty]
        e.g.
        0.2.dev34+new.shiny.feature.gfa973da
        2.5.dev7+master.gb91ffa6.dirty

    - for UNKNOWN builds:
        0.0+unknown.[<scm_type>.]<timestamp>
        e.g.
        0.0+unknown.svn.201402031023
        0.0+unknown.201602081715

    where <major>.<minor> is derived from the latest version tag and
    <num_commits> is the total number of commits on the development branch.

    The <major>.<minor> substring for development builds will be that of the
    NEXT (minor) release, in order to allow proper Python version ordering.

    To add a version tag use the `git tag` command, e.g.

        $ git tag -a 1.2 -m 'Release version 1.2'

Typical Usage
-------------

Add this to ``setup.py`` (handles installed packages):

.. code:: python

        from setuptools import setup

        setup(
            ...,
            setup_requires=['katversion'],
            use_katversion=True,
            ...
        )

Add this to ``mypackage/__init__.py``, including the comment lines
(handles local packages):

.. code:: python

        # BEGIN VERSION CHECK
        # Get package version when locally imported from repo or via -e develop install
        try:
            import katversion as _katversion
        except ImportError:
            import time as _time
            __version__ = "0.0+unknown.{}".format(_time.strftime('%Y%m%d%H%M'))
        else:
            __version__ = _katversion.get_version(__path__[0])
        # END VERSION CHECK

In addition, a command-line script for checking the version:

::

        # From inside your SCM subdirectory, run the following command
        # which will print the result to stdout:
        $ kat-get-version.py
