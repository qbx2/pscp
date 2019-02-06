![TravisCI](https://img.shields.io/travis/qbx2/pscp/master.svg?style=flat)
[![PyPI](https://img.shields.io/pypi/v/pscp.svg?style=flat)](https://pypi.org/project/pscp/)
![PyPI-License](https://img.shields.io/pypi/l/pscp.svg?style=flat)
![PyPI-Python-Versions](https://img.shields.io/pypi/pyversions/pscp.svg?style=flat)

# PSCP: Per-session checkpoint

### Author: Sunyeop Lee (sunyeop97 at gmail.com)

### Requirements

* python 3.5+
* git

Use .gitignore to avoid stashing unnecessary files.

### Command Line Tool (TODO)

`python -m pscp`

### `pscp.create(return_head_on_nothing=True, return_format='abbrev', link=True)`

Create per-session checkpoint.

* `return_head_on_nothing`: When there are nothing changed compared to HEAD, return hash of HEAD if True, otherwise, return `None`.
* `return_format`
	* `abbrev`, `short`: Return abbreviated hash.
	* `long`: Return just unabbreviated hash.
	* `ref`: Return refspec. Raises exception when link == False.
* `link`: See `pscp.link()` below.

### `pscp.link(hash)`

Create reference named `refs/checkpoints/{timestamp}`. It could be used to avoid pruning on garbage collection.

### `pscp.delete(refspec, run_gc=False)`

Delete pscp reference.

* `refspec`: Target refspec to be deleted.
* `run_gc`: If true, run `git gc --prune=now`. Otherwise, objects might be still alive.

### `pscp.push(refspec=None, refmap=None, repository='origin')`

Push checkpoint to the remote repository.

* `refspec`: If `None`, all checkpoints are pushed.

### `pscp.fetch(refspec=None, refmap=None, repository='origin')`

* `refspec`: If `None`, all checkpoints are fetched.
* `refmap`: If `None`, `refs/checkpoints/*:refs/checkpoints/*` is used.

## How does it work?

### Tutorial: How to store the source code on every session to check-out or diff later - using `git-stash-create`


When I study, I always feel like *saving the source code somewhere on each run, and then check out to it later or see the difference of the runs.*

## Old-fashion method: using git-commit

To achieve, I had logged every git commit hashes to tensorboard session. However, this way made me tired to write commit messages to every session. I lost the detailed history each time I skip it. What was worse, it made my commit log dirty -- change learning rate to xx, change beta to yy, ...

## Using git-stash-create for boosting up your research

I thought some method that could store the current workspace with unstaged files, which would neither require commit message nor let my git log dirty. There is a command, `git stash create`, which creates a dangling commit with staged, unstaged files and outputs hash of the commit. This was the excellent fit for the problem.

Using git-stash-create inherits all strengths from git, which are very useful for study.

* Recycle unchanged objects
* Compression (zlib)
* Show differences using `git diff a..b`
* Checkout to, using `git checkout`
* Create branch from, using `git stash branch ...` This restores staged files staged and unstaged files unstaged.

You also could stage untracked new files to include in `git stash create` using `git add`.

### Example

Initialize git repository for example.

```
$ mkdir example && cd example

$ git init
Initialized empty Git repository in /home/qbx2/example/.git/

$ echo LEARNING_RATE=0.5 > config.txt

$ git add config.txt && git commit -m "Initial commit"
[master (root-commit) 96a145e] Initial commit
 1 file changed, 1 insertion(+)
 create mode 100644 config.txt
```

Make some changes and create stashes (per-session checkpoints).

```
$ echo LEARNING_RATE=0.3 > config.txt
$ git stash create
2741da39b09687a06acd71651ce26eded3458606

$ echo LEARNING_RATE=0.1 > config.txt
$ git stash create
5bbe8a5d956ad5176915e231750c3cc98511d622
```

`git stash create` does not make neither git-log nor git-stash-list dirty.

```
$ git log | cat
commit 96a145e2f20eb08b9b838f7424cfba5afdca56bc
Author: Sunyeop Lee <sunyeop97@gmail.com>
Date:   Fri Feb 1 14:38:03 2019 +0900

    Initial commit

$ git stash list | cat
```

Log the outputs of `git stash create` in other way to reference them later. Then, we can see difference using `git diff`.

```
$ git diff 2741da..5bbe8a | cat
diff --git a/config.txt b/config.txt
index 214f551..7bc7046 100644
--- a/config.txt
+++ b/config.txt
@@ -1 +1 @@
-LEARNING_RATE=0.3
+LEARNING_RATE=0.1
```

We could check-out to a new branch using `git stash branch`. This command will restore staged files staged too.

```
$ git reset --hard && git stash branch test-restore 2741da39b09687a06acd71651ce26eded3458606
HEAD is now at 96a145e Initial commit
Switched to a new branch 'test-restore'
On branch test-restore
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git checkout -- <file>..." to discard changes in working directory)

	modified:   config.txt

no changes added to commit (use "git add" and/or "git commit -a")
```

## Using git-update-ref to avoid from being pruned

Because `git stash create` does not store the commit anywhere in the ref namespace, there is possibility to be pruned on `git gc`(or `git prune`) which is automatically executed by some commands.

For example,

```
$ git show 2741da39b09687a06acd71651ce26eded3458606 | cat
commit 2741da39b09687a06acd71651ce26eded3458606
... (omitted)

$ git gc --prune=now
Counting objects: 3, done.
Writing objects: 100% (3/3), done.
Total 3 (delta 0), reused 0 (delta 0)

$ git show 2741da39b09687a06acd71651ce26eded3458606 | cat
fatal: bad object 2741da39b09687a06acd71651ce26eded3458606
```

By storing the commit in refs, now it's safe.

(`<checkpoint_id>` is the output when executed `git stash create`)
`git update-ref "refs/checkpoints/$(date +%s)" <checkpoint_id>`

You can see the created/updated reference using `git show-ref` command.

```
$ git update-ref "refs/checkpoints/$(date +%s)" 2741da39b09687a06acd71651ce26eded3458606
$ git show-ref
96a145e2f20eb08b9b838f7424cfba5afdca56bc refs/heads/master
2741da39b09687a06acd71651ce26eded3458606 refs/checkpoints/1548995645

$ git show 2741da39b09687a06acd71651ce26eded3458606 | cat
commit 2741da39b09687a06acd71651ce26eded3458606
... (omitted)
```

## Pushing to remote repository

We've named `git-stash-create`-ed commits using `git-update-ref`, now we can push them to the remote repository. For example, I set my github repository as remote origin.

```
$ git push origin 'refs/checkpoints/*'
Total 0 (delta 0), reused 0 (delta 0)
To https://github.com/qbx2/test
 * [new branch]      refs/checkpoints/1548995645 -> refs/checkpoints/1548995645
```

`git push` says new branch is created but it's not a branch because we specified destination reference in `refs/checkpoints/` not `refs/heads/`. That's why we cannot see the checkpoint in the github repository branches. To see, visit `<github repository>/tree/refs/checkpoints/1548995645`. Also, `git ls-remote` shows that your remote references.

```
$ git ls-remote
From https://github.com/qbx2/test
96a145e2f20eb08b9b838f7424cfba5afdca56bc HEAD
96a145e2f20eb08b9b838f7424cfba5afdca56bc refs/heads/master
2741da39b09687a06acd71651ce26eded3458606 refs/checkpoints/1548995645
```

When we have low disk space, we might want to save space by pruning pushed checkpoints.
First, delete the reference we've created to avoid pruning.

```
$ git update-ref refs/checkpoints/1548995645 -d
$ git show-ref
96a145e2f20eb08b9b838f7424cfba5afdca56bc refs/heads/master
96a145e2f20eb08b9b838f7424cfba5afdca56bc refs/remotes/origin/master
```

Still, the object is alive.

```
$ git show 2741da39b09687a06acd71651ce26eded3458606 | cat
commit 2741da39b09687a06acd71651ce26eded3458606
Merge: 7ed4dec ff70b7e
Author: Sunyeop Lee <sunyeop97@gmail.com>
Date:   Fri Feb 1 12:26:54 2019 +0900

    WIP on master: 7ed4dec test

    ... (omitted)
```

Prune it by `git gc --prune=now`.

```
$ git gc --prune=now
Counting objects: 10, done.
Delta compression using up to 16 threads.
Compressing objects: 100% (5/5), done.
Writing objects: 100% (10/10), done.
Total 10 (delta 1), reused 10 (delta 1)

$ git show 2741da39b09687a06acd71651ce26eded3458606 | cat
fatal: bad object 2741da39b09687a06acd71651ce26eded3458606
```

## Fetching from remote repository

My local git repository does not know about `f0951fe`, which is pruned. However, we can fetch them whenever we want to because we've pushed it to the remote repository.

To create local reference, `--refmap` is given.

```
$ git ls-remote origin 'refs/checkpoints/*'
2741da39b09687a06acd71651ce26eded3458606    refs/checkpoints/1548995645

$ git fetch origin refs/checkpoints/1548995645 --refmap 'refs/checkpoints/*:refs/checkpoints/*'
```

To fetch multiple refs,

```
$ git fetch origin 'refs/checkpoints/*:refs/checkpoints/*'
```
