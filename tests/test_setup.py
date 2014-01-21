from squadron import setup
import os

def test_system(tmpdir):
    tmpdir = str(tmpdir)
    etcdir = os.path.join(tmpdir, 'etc', 'squadron')
    vardir = os.path.join(tmpdir, 'var', 'squadron')

    setup.init_system(etcdir, vardir)

    assert os.path.exists(os.path.join(etcdir, 'config'))
    assert os.path.exists(os.path.join(vardir, 'info.json'))

