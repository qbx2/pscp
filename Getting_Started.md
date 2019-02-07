# Getting Started with PSCP

[ipynb version](Getting_Started.ipynb)

## Requirements

* python 3.5+
* git
* pscp
* [tensorboard](https://github.com/tensorflow/tensorboard)
* [tensorboardX](https://github.com/lanpa/tensorboardX)

### Install pscp and tensorboardX

    $ pip install pscp==0.0.2 tensorboardX==1.6

### Install tensorboard

    $ pip install tensorboard

or if have docker:

    $ docker pull tensorflow/tensorflow

and run by:

    $ docker run -i -p 6006:6006 -v "$(pwd)/logdir":/logdir tensorflow/tensorflow tensorboard --logdir /logdir

`tensorboardX` is a python library that can write sessions for tensorboard.

## Tutorial

Initialize git repository.
PSCP requires single commit at least.

```bash
$ git init
$ git config user.email example@example.com  # not needed if set already
$ echo LEARNING_RATE_OR_WHATEVER=0.1 > config.txt
$ git add config.txt && git commit -m "Initial commit"

Initialized empty Git repository in /content/.git/
[master (root-commit) 1ba5822] Initial commit
 1 file changed, 1 insertion(+)
 create mode 100644 config.txt
```

Make a change to config.txt

```bash
$ echo LEARNING_RATE_OR_WHATEVER=0.05 > config.txt
```

Import libraries.

`math` is just for `sin` and `pi`.

```python
from math import sin, pi

import pscp
import tensorboardX
```

Create checkpoint. (outputs 757fad0 in this time)

```python
h = pscp.create()
print(h)
```

Create SummaryWriter, using hash-concatenated session name.

```python
writer = tensorboardX.SummaryWriter('logdir/some-session-{}'.format(h))
```

Log metrics using writer. For details, please refer to [tensorboardX](https://github.com/lanpa/tensorboardX).

```python
for step in range(400):
    sin_step = sin(step * pi / 180.)
    writer.add_scalar('pscp_example/sin_step', sin_step, step)

writer.close()
```

Now, let's see the output.

```bash
$ ls -l
...
drwxr-xr-x 3 root root 4096 Feb  7 06:22 logdir

$ ls -l logdir/
total 4
drwxr-xr-x 2 root root 4096 Feb  7 06:22 some-session-52022f5

$ git show 757fad0 # the output from pscp.create()

$ tensorboard --logdir ./logdir
```

We would be able to see the checkpoint hash of each session in `Runs`.
Make a change to config.txt, any scripts, or any tracked files and re-run the script to create another session.

For demonstration, we're just going to change config.txt and `pscp.create()`.

```bash
$ echo LEARNING_RATE_OR_WHATEVER=0.01 > config.txt
$ python -c "import pscp; print(pscp.create())"

df403bf
```

```
$ git show df403bf

commit df403bf1f08cd64eab4943dc83a4637e75e746fc (refs/pscp/1549521824490)
Merge: 1ba5822 f3c34c7
Author: root <example@example.com>
Date:   Thu Feb 7 06:43:44 2019 +0000

    WIP on master: 1ba5822 Initial commit

diff --cc config.txt
index fbb1eb2,fbb1eb2..d36cf89
--- a/config.txt
+++ b/config.txt
@@@ -1,1 -1,1 +1,1 @@@
--LEARNING_RATE_OR_WHATEVER=0.1
++LEARNING_RATE_OR_WHATEVER=0.01
```

And then, we now know two checkpoint hashes.
Let's see how we can see diff of these.

```bash
$ git diff 757fad0..df403bf

diff --git a/config.txt b/config.txt
index 7b141ac..d36cf89 100644
--- a/config.txt
+++ b/config.txt
@@ -1 +1 @@
-LEARNING_RATE_OR_WHATEVER=0.05
+LEARNING_RATE_OR_WHATEVER=0.01
```

Also, we can use `git stash branch` and `git checkout` on it.