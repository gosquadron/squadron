from . import schema, verify, apply
import os
import logging
import mock

log = logging.getLogger('normal')

test_path = os.path.dirname(os.path.realpath(__file__))

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def test_schema():
    assert isinstance(schema(), dict)

def test_verify():
    with mock.patch('subprocess.Popen') as popen:
        p = mock.MagicMock()
        p.communicate.return_value = (read_file(os.path.join(test_path, 'list.txt')), None)
        p.wait.return_value = 0

        popen.return_value = p

        result = verify(['ignore','ignore-ver@0.0.1', 'not-installed',
            'not-installed2@0.0.1'], log)

        assert result == ['not-installed', 'not-installed2@0.0.1']
        p.communicate.assert_called_with()
        p.wait.assert_called_with()


def test_apply():
    with mock.patch('subprocess.call') as call:
        def fail_particular(which):
            def fail_first(args):
                assert 'npm' in args
                assert 'install' in args
                assert '--global' in args

                if which in args:
                    return 1
                else:
                    return 0
            return fail_first


        args = ['failthis', 'works@0.0.1']

        call.side_effect = fail_particular(args[0])

        result = apply(args, log)
        assert result == [args[0]]

        for arg in args:
            call.assert_any_call(['npm', 'install', arg, '--global'])
