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
            ('git', 'stash', 'create'), capture_output=True)

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

    @patch('pscp.pscp._run_git')
    def test_create(self, run_git):
        run_git.return_value = 'test hash 123'

        output = pscp.create(return_format='long', link=False)

        self.assertEqual(output, 'test hash 123')
        run_git.assert_called_once_with('stash', 'create')

    def test_create_invalid_return_format_raise(self):
        with self.assertRaises(ValueError):
            pscp.create(return_format='invalid return format')

    @patch('pscp.pscp._run_git')
    def test_create_nothing(self, run_git):
        def side_effect(*args):
            if args == ('stash', 'create'):
                return ''

            if args == ('rev-parse', 'HEAD'):
                return 'test head hash 456'

        run_git.side_effect = side_effect

        output = pscp.create(return_format='long', link=False)

        self.assertEqual(output, 'test head hash 456')

    @patch('pscp.pscp._run_git')
    def test_create_short(self, run_git):
        def side_effect(*args):
            if args == ('stash', 'create'):
                return 'test long long hash abcdef'

            if args == ('rev-parse', '--short', 'test long long hash abcdef'):
                return 'test short hash abc'

        run_git.side_effect = side_effect

        output1 = pscp.create(return_format='abbrev', link=False)
        output2 = pscp.create(return_format='short', link=False)

        self.assertEqual(output1, 'test short hash abc')
        self.assertEqual(output2, 'test short hash abc')

    def test_create_ref_link_false_raise(self):
        with self.assertRaises(ValueError):
            pscp.create(return_format='ref', link=False)

    @patch('pscp.pscp._link')
    @patch('pscp.pscp._run_git')
    def test_create_ref_link(self, run_git, link):
        run_git.return_value = h = 'test hash 123'
        link.return_value = 'ref/checkpoints/123456'

        output = pscp.create(return_format='ref', link=True)

        link.assert_called_once_with(h)
        self.assertEqual(output, 'ref/checkpoints/123456')

    @patch('pscp.pscp._link')
    @patch('pscp.pscp._run_git')
    def test_create_no_link_nothing(self, run_git, link):
        run_git.return_value = None

        output1 = pscp.create(return_head_on_nothing=True, link=True)
        output2 = pscp.create(return_head_on_nothing=False, link=True)

        link.not_assert_called()
        self.assertEqual(output1, None)
        self.assertEqual(output2, None)
