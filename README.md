[![TravisCI](https://img.shields.io/travis/qbx2/pscp/master.svg?style=flat)](https://travis-ci.org/qbx2/pscp/)
[![PyPI](https://img.shields.io/pypi/v/pscp.svg?style=flat)](https://pypi.org/project/pscp)
![PyPI-License](https://img.shields.io/pypi/l/pscp.svg?style=flat)

# PSCP: Per-session checkpoint

PSCP is a brand-new way to make checkpoint in git repository efficiently.
By logging the hash output by `pscp.create()`, you can `git diff`, `git stash branch` and `git checkout` using them whenever you want.
PSCP is framework-agnostic, so can be used in any git repository.

PSCP inherits all strengths from git, which are very useful for study.

* Recycle unchanged objects
* Compression (zlib)
* Show differences using `git diff a..b`
* Checkout to, using `git checkout`
* Create branch from, using `git stash branch`. This restores staged files staged and unstaged files unstaged.

Besides, PSCP does make neither `git log` nor `git stash list` messy. You won't suffer from trivial tuning commits and too many stashes.

## Requirements

* python 3.5+
* git

## Installation

`pip install pscp`

## Getting Started (with [tensorboardX](https://github.com/lanpa/tensorboardX))

[Getting Started](Getting_Started.md)

## How does it work?

[How It Works](How_It_Works.md)

## Frequently Asked Questions

### Tracking New Files

Use `git add` to stage, to track new files. Untracked files will not be added to the checkpoint.

### Saving environment variables or argparse results?

You're supposed to write to any file and track them (using `git add`).
Using json built-in library, it can be done easily.

```python
import json
```

To save environment variables,

```python
import os
json.dump(fp, dict(os.environ), indent=4)
```

To save argparse namespace,

```python
json.dump(fp, vars(args), indent=4)
```

Any other data can be saved in same way.

## Command Line Tool (TODO)

`python -m pscp`

## pscp.create(return\_head\_on\_nothing=True, return\_format='abbrev', link=True)

Create per-session checkpoint.

* `return_head_on_nothing`: If True, return hash of `HEAD` when there are nothing changed compared to `HEAD`, otherwise, return `None`.
* `return_format`
	* `abbrev`, `short`: Return abbreviated hash.
	* `long`: Return just unabbreviated hash.
	* `ref`: Return refspec. Raises exception when link == False.
* `link`: See `pscp.link()` below.

## pscp.link(hash, refspec=None)

Create reference. `pscp.link()` could be used to avoid pruning on garbage collection.

* `hash`: The hash to be referenced.
* `refspec`: If `None`, `refs/pscp/{timestamp_ms}` is used.

## pscp.delete(refspec)

Delete pscp reference. Call `pscp.gc()` if you want.

* `refspec`: Target refspec to be deleted. `timestamp_ms` is also allowed.

## pscp.gc(prune='now')

Run `git gc --prune=<prune>`.

## pscp.push(refspec=None, repository='origin')

Push checkpoint to the remote repository.

* `refspec`: If `None`, all checkpoints are pushed.

## pscp.fetch(refspec=None, refmap=None, repository='origin')

* `refspec`: If `None`, all checkpoints are fetched.
* `refmap`: If `None`, `refs/pscp/*:refs/pscp/*` is used.
