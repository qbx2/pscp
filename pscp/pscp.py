# Author: Sunyeop Lee <sunyeop97@gmail.com>
import subprocess


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
    p = subprocess.run(args, capture_output=True)

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


def _link(h):
    raise NotImplementedError


link = _link
