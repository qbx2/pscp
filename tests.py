from unittest import TestCase
from unittest.mock import patch

import pscp.pscp as pscp


class TestPSCP(TestCase):
    @patch('subprocess.run')
    def test_run_git_return(self, run):
        run.return_value.stdout = b'test hash 123\n'
        run.return_value.stderr = b''
        run.return_value.returncode = 0

        output = pscp._run_git('stash', 'create')

        self.assertEqual(output, 'test hash 123')
        run.assert_called_once_with(
            ['git', 'stash', 'create'], capture_output=True)

    @patch('subprocess.run')
    def test_run_git_return_invalid_characters(self, run):
        run.return_value.stdout = b'unknown hash 123\xff\xfe\xee\n'
        run.return_value.stderr = b''
        run.return_value.returncode = 0

        output = pscp._run_git('test')

        self.assertEqual(output, 'unknown hash 123\uFFFD\uFFFD\uFFFD')

    @patch('subprocess.run')
    def test_run_git_raise(self, run):
        run.return_value.stdout = b''
        run.return_value.stderr = b'test error'
        run.return_value.returncode = 1

        with self.assertRaises(pscp.CalledProcessError) as cm:
            pscp._run_git('test')

        e = cm.exception

        self.assertEqual(e.returncode, 1)
        self.assertEqual(e.stdout, b'')
        self.assertEqual(e.stderr, b'test error')
