# Author: Sunyeop Lee <sunyeop97@gmail.com>
import subprocess
import time

REF_NAMESPACE = 'pscp'


class CalledProcessError(Exception):
    def __init__(self, p):
        super().__init__(p)

        self.returncode = p.returncode
        self.stdout = p.stdout
        self.stderr = p.stderr

        self.message = \
            'Command {} returned non-zero exit status {}.\n'.format(
                p.args, p.returncode)

        if p.stdout:
            self.message += \
                'stdout: {}\n'.format(p.stdout.decode(errors='replace'))

        if p.stderr:
            self.message += \
                'stderr: {}\n'.format(p.stderr.decode(errors='replace'))

        self.message = self.message.rstrip()

    def __str__(self):
        return self.message


def _run_git(*git_args):
    args = ('git', *git_args)

    if not all(isinstance(arg, str) for arg in args):
        raise TypeError('Expected all to be str, got {}'.format(
            tuple(map(type, git_args))))

    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if p.returncode:
        raise CalledProcessError(p)

    return p.stdout.decode(errors='replace').strip()


def create(return_head_on_nothing=True, return_format='abbrev', link=True):
    if return_format not in ('abbrev', 'short', 'long', 'ref'):
        raise ValueError('Unknown return_format: {}'.format(return_format))

    if not link and return_format == 'ref':
        raise ValueError('link must be True when return_format="ref"')

    h = _run_git('stash', 'create')

    if not h and return_head_on_nothing:
        h = _run_git('rev-parse', 'HEAD')

    if h and link:
        ref = _link(h)
    else:
        ref = None

    if return_format in ('abbrev', 'short'):
        return_value = _run_git('rev-parse', '--short', h)
    elif return_format == 'long':
        return_value = h
    elif return_format == 'ref':
        return_value = ref

    return return_value or None


def link(h):
    if not isinstance(h, str):
        raise TypeError('Expected str, not {}'.format(type(h)))

    timestamp_ms = int(time.time() * 1000)
    ref = 'refs/{}/{}'.format(REF_NAMESPACE, timestamp_ms)
    _run_git('update-ref', ref, h)

    return ref


_link = link


def delete(refspec):
    if not isinstance(refspec, str):
        raise TypeError('Expected str, not {}'.format(type(refspec)))

    prefix = 'refs/{}/'.format(REF_NAMESPACE)

    if '/' not in refspec:
        refspec = prefix + refspec
    elif not refspec.startswith(prefix):
        raise ValueError('Expected refspec to start with {}'.format(prefix))

    _run_git('update-ref', '-d', refspec)


def gc(prune='now'):
    if not isinstance(prune, str):
        raise TypeError('Expected str, not {}'.format(type(prune)))

    return _run_git('gc', '--prune={}'.format(prune))


def push(refspec=None, repository='origin'):
    if refspec is None:
        refspec = 'refs/{}/*'.format(REF_NAMESPACE)

    if not isinstance(refspec, str):
        raise TypeError('Expected str or None, not {}'.format(type(refspec)))

    if not isinstance(repository, str):
        raise TypeError('Expected str or None, not {}'.format(
            type(repository)))

    _run_git('push', repository, refspec)


def fetch(refspec=None, refmap=None, repository='origin'):
    git_fetch_args = [repository]

    if refmap is None:
        refmap = ':'.join(['refs/{}/*'.format(REF_NAMESPACE)] * 2)
    elif not isinstance(refmap, str):
        raise TypeError('Expected str or None, not {}'.format(type(refmap)))

    if not isinstance(repository, str):
        raise TypeError('Expected str or None, not {}'.format(
            type(repository)))

    if refspec is None:
        git_fetch_args.append(refmap)
    elif isinstance(refspec, str):
        git_fetch_args += [refspec, '--refmap', refmap]
    else:
        raise TypeError('Expected str or None, not {}'.format(type(refspec)))

    _run_git('fetch', *git_fetch_args)
