from squadron import setup
import os
import mock

def test_system(tmpdir):
    tmpdir = str(tmpdir)
    etcdir = os.path.join(tmpdir, 'etc', 'squadron')
    vardir = os.path.join(tmpdir, 'var', 'squadron')

    setup.init_system(etcdir, vardir)

    assert os.path.exists(os.path.join(etcdir, 'config'))
    assert os.path.exists(os.path.join(vardir, 'info.json'))

def test_setup(tmpdir):
    tmpdir = str(tmpdir)
    etcdir = os.path.join(tmpdir, 'first', 'etc', 'squadron')
    vardir = os.path.join(tmpdir, 'first', 'var', 'squadron')

    with mock.patch('__builtin__.raw_input', side_effect=[etcdir, vardir]):
        setup.setup(None, None)
        assert os.path.exists(os.path.join(etcdir, 'config'))
        assert os.path.exists(os.path.join(vardir, 'info.json'))

    etcdir = os.path.join(tmpdir, 'second', 'etc', 'squadron')
    vardir = os.path.join(tmpdir, 'second', 'var', 'squadron')
    with mock.patch('__builtin__.raw_input', return_value=etcdir):
        setup.setup(None, vardir)
        assert os.path.exists(os.path.join(etcdir, 'config'))
        assert os.path.exists(os.path.join(vardir, 'info.json'))

    etcdir = os.path.join(tmpdir, 'third', 'etc', 'squadron')
    vardir = os.path.join(tmpdir, 'third', 'var', 'squadron')
    with mock.patch('__builtin__.raw_input', return_value=vardir):
        setup.setup(etcdir, None)
        assert os.path.exists(os.path.join(etcdir, 'config'))
        assert os.path.exists(os.path.join(vardir, 'info.json'))

    etcdir = os.path.join(tmpdir, 'fourth', 'etc', 'squadron')
    vardir = os.path.join(tmpdir, 'fourth', 'var', 'squadron')
    with mock.patch('__builtin__.raw_input', side_effect=Exception('Don\'t call this')):
        setup.setup(etcdir, vardir)
        assert os.path.exists(os.path.join(etcdir, 'config'))
        assert os.path.exists(os.path.join(vardir, 'info.json'))
