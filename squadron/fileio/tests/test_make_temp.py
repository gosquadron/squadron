import os
from ..make_temp import make_temp

def test_basic_temp(tmpdir):
    tmpdir = str(tmpdir)

    print tmpdir
    for i in range(100):
        assert os.path.exists(make_temp(tmpdir, 'test_basic_temp-'))

    dirs = os.listdir(tmpdir)
    assert len(dirs) == 7
    assert 'test_basic_temp-99' in dirs

def test_keep_temp(tmpdir):
    tmpdir = str(tmpdir)

    print tmpdir
    keep_this = os.path.join(tmpdir, 'test_keep_temp-5')
    for i in range(100):
        assert os.path.exists(make_temp(tmpdir, 'test_keep_temp-', keep_this))

    dirs = os.listdir(tmpdir)
    assert len(dirs) == 8
    assert 'test_keep_temp-5' in dirs
    assert 'test_keep_temp-6' not in dirs
