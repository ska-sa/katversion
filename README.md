katversion
==========

Provides proper versioning for python packages.

Versioning
----------
*katversion* generates a version string for your SCM package that complies with
[PEP440] (http://legacy.python.org/dev/peps/pep-0440/).

The format of our version string is:

    - for RELEASE builds:
        <major>.<minor>
        e.g.
        0.1
        2.4

    - for DEVELOPMENT builds:
        <major>.<minor>.dev<num_branch_commits>+<branch_name>.<short_git_sha>[-dirty]
        e.g.
        1.1.dev34+new_shiny_feature.efa973da
        0.1.dev7+master.gb91ffa6-dirty
    
    where <major>.<minor> is derived from the latest version tag.
    
    To add a version tag use the `git tag` command, e.g.
    
        $ git tag -a 1.2 -m 'Release version 1.2'

Typical usage in `setup.py`:

```python
    from katversion import get_version

    setup(
        ...,
        version=get_version(),
        ...
    )
```

Typical usage from command line:

```
    # From somewhere inside your SCM, run the next command, it will print 
    # the result to stdout.
    $ kat-get-version.py
    
    # Or for a release version (without all the development details)
    $ kat-get-version.py -r
```
