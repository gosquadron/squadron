import os
from ..virtualenv import ext_virtualenv
from stat import *

def test_basic(tmpdir):
    tmpdir = str(tmpdir)

    abs_source = os.path.join(tmpdir, 'requirements.txt')
    with open(abs_source, 'w') as vfile:
        vfile.write('bottle\n')
        vfile.write('pytest\n')

    dest = os.path.join(tmpdir, 'env~virtualenv')
    finalfile = ext_virtualenv(abs_source, dest)

    assert os.path.exists(finalfile)
    assert os.path.exists(os.path.join(finalfile, 'bin', 'activate'))

    python = os.path.join(finalfile, 'bin', 'python')
    assert os.path.exists(python)
    st = os.stat(python)

    # Make sure Python is executable
    assert st.st_mode & S_IXUSR > 0
    assert st.st_mode & S_IXGRP > 0
    assert st.st_mode & S_IXOTH > 0

    lib_dir = os.path.join(finalfile, 'lib', 'python2.7',
                'site-packages')
    assert os.path.exists(os.path.join(lib_dir, 'bottle.py'))
    assert os.path.exists(os.path.join(lib_dir, 'pytest.py'))
