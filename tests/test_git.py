import os
from squadron.exthandlers.makegit import _set_ssh_wrapper, _get_ssh_wrapper, ext_git
from quik import FileLoader
import pytest
import git

def get_loader():
    return FileLoader(os.getcwd())

def test_basic(tmpdir):
    tmpdir = str(tmpdir)

    abs_source = os.path.join(tmpdir, 'deploy~git')
    with open(abs_source, 'w') as gfile:
        gfile.write('https://github.com/cxxr/test-git-repo.git\n')

    dest = os.path.join(tmpdir, 'dest-dir')

    finalfile = ext_git(abs_source, dest, {}, get_loader(), {})

    assert os.path.exists(finalfile)
    assert os.path.exists(os.path.join(finalfile, '.git'))
    assert os.path.exists(os.path.join(finalfile, '.git', 'config'))
    assert os.path.exists(os.path.join(finalfile, 'install'))

def test_refspec(tmpdir):
    tmpdir = str(tmpdir)

    abs_source = os.path.join(tmpdir, 'deploy~git')
    with open(abs_source, 'w') as gfile:
        gfile.write('https://github.com/cxxr/test-git-repo.git @version\n')

    dest = os.path.join(tmpdir, 'dest-dir')

    finalfile = ext_git(abs_source, dest, {'version':'a057eb0faaa8'}, get_loader(), {})

    assert os.path.exists(finalfile)
    assert os.path.exists(os.path.join(finalfile, '.git'))
    assert os.path.exists(os.path.join(finalfile, '.git', 'config'))
    install_file = os.path.join(finalfile, 'install')
    assert os.path.exists(install_file)

    with open(install_file) as ifile:
        assert ifile.read().strip() == 'echo "Success"'

def test_sshkey(tmpdir):
    tmpdir = str(tmpdir)

    # we need to do this to avoid ssh-agent problems
    ssh = _get_ssh_wrapper().format('{} -o IdentitiesOnly=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null','{}')
    _set_ssh_wrapper(ssh)
    assert _get_ssh_wrapper() == ssh

    test_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(test_path, 'private_key')) as k:
        private_key = k.read()

    abs_source = os.path.join(tmpdir, 'deploy~git')
    dest = os.path.join(tmpdir, 'dest-dir')

    with open(abs_source, 'w') as gfile:
        gfile.write('git@bitbucket.org:test-squadron/test-private-repo.git @version\n')

    with pytest.raises(git.GitCommandError) as ex:
        finalfile = ext_git(abs_source, dest, {'version':'a057eb0faaa8'}, get_loader(),
                {'filename': lambda: private_key})

    assert 'access denied' in str(ex) or 'Permission denied' in str(ex)

    with open(abs_source, 'w') as gfile:
        gfile.write('git@bitbucket.org:test-squadron/test-private-repo.git @version filename\n')

    dest = os.path.join(tmpdir, 'dest-dir2')
    finalfile = ext_git(abs_source, dest, {'version':'a057eb0faaa8'}, get_loader(),
            {'filename': lambda: private_key})
    print finalfile
