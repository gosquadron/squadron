import os
from ..makegit import ext_git

def test_basic(tmpdir):
    tmpdir = str(tmpdir)

    abs_source = os.path.join(tmpdir, 'deploy~git')
    with open(abs_source, 'w') as gfile:
        gfile.write('https://github.com/cxxr/test-git-repo.git\n')

    dest = os.path.join(tmpdir, 'dest-dir')

    finalfile = ext_git(abs_source, dest)

    assert os.path.exists(finalfile)
    assert os.path.exists(os.path.join(finalfile, '.git'))
    assert os.path.exists(os.path.join(finalfile, '.git', 'config'))
    assert os.path.exists(os.path.join(finalfile, 'install'))

def test_refspec(tmpdir):
    tmpdir = str(tmpdir)

    abs_source = os.path.join(tmpdir, 'deploy~git')
    with open(abs_source, 'w') as gfile:
        gfile.write('https://github.com/cxxr/test-git-repo.git a057eb0faaa8\n')

    dest = os.path.join(tmpdir, 'dest-dir')

    finalfile = ext_git(abs_source, dest)

    assert os.path.exists(finalfile)
    assert os.path.exists(os.path.join(finalfile, '.git'))
    assert os.path.exists(os.path.join(finalfile, '.git', 'config'))
    install_file = os.path.join(finalfile, 'install')
    assert os.path.exists(install_file)

    with open(install_file) as ifile:
        assert ifile.read().strip() == 'echo "Success"'
