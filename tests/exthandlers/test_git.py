import os
from squadron.exthandlers.makegit import ext_git
from quik import FileLoader
import pytest
import git
import mock

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


@pytest.mark.parametrize("ssh_command", [None, "fake_ssh_command"])
def test_sshkey(tmpdir,ssh_command):
    tmpdir = str(tmpdir)

    test_path = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(test_path, 'private_key')) as k:
        private_key = k.read()

    abs_source = os.path.join(tmpdir, 'deploy~git')
    dest = os.path.join(tmpdir, 'dest-dir')

    with mock.patch('git.Repo') as gitmock:
        # We need a side effect to see if the env variable is being set
        def check_environ(*args):
            if ssh_command:
                with open(os.environ['GIT_SSH']) as gitfile:
                    if ssh_command not in gitfile.read():
                        assert False
            # We need to return a mock handle so .git.checkout can be called
            return gitmock.clone_from

        # Apply the side effect
        gitmock.clone_from.side_effect = check_environ

        # Since this is mocked, it won't actually be hit
        url = 'git@example.org:squadron/test-repo.git'
        version = 'a057eb0faaa8'
        with open(abs_source, 'w') as gfile:
            gfile.write(url + ' @version filename\n')

        dest = os.path.join(tmpdir, 'dest-dir2')

        # If we have a special ssh_command to use, use it
        if ssh_command:
            os.environ['GIT_SSH'] = ssh_command

        finalfile = ext_git(abs_source, dest, {'version':version}, get_loader(),
                {'filename': lambda: private_key})

        expected_calls = [mock.call.clone_from(url, finalfile),
                mock.call.clone_from.git.checkout(version)]
        assert expected_calls == gitmock.mock_calls
        if ssh_command:
            assert 'GIT_SSH' in os.environ
            assert os.environ['GIT_SSH'] == ssh_command
        else:
            assert 'GIT_SSH' not in os.environ
