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
    args = ['git', *git_args]
    p = subprocess.run(args, capture_output=True)

    if p.returncode:
        raise CalledProcessError(p)

    return p.stdout.decode(errors='replace').strip()
