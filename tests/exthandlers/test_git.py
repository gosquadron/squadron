import os
import squadron
from squadron.exthandlers.makegit import ext_git
from quik import FileLoader
import pytest
import git
import mock
import json

def get_loader():
    return FileLoader(os.getcwd())

def get_git_file(url, refspec = None, sshkey = None, args = None):
    obj = {'url': url}

    if refspec:
        obj['refspec'] = refspec
    if sshkey:
        obj['sshkey'] = sshkey
    if args:
        obj['args'] = args

    return json.dumps(obj)

@pytest.mark.timeout(10)
def test_basic(tmpdir):
    tmpdir = str(tmpdir)

    abs_source = os.path.join(tmpdir, 'deploy~git')
    with open(abs_source, 'w') as gfile:
        gfile.write(get_git_file('https://github.com/cxxr/test-git-repo.git'))

    dest = os.path.join(tmpdir, 'dest-dir')

    finalfile = ext_git(abs_source, dest, {}, get_loader(), {})

    assert os.path.exists(finalfile)
    assert os.path.exists(os.path.join(finalfile, '.git'))
    assert os.path.exists(os.path.join(finalfile, '.git', 'config'))
    assert os.path.exists(os.path.join(finalfile, 'install'))

@pytest.mark.timeout(10)
def test_refspec(tmpdir):
    tmpdir = str(tmpdir)

    abs_source = os.path.join(tmpdir, 'deploy~git')
    with open(abs_source, 'w') as gfile:
        gfile.write(get_git_file('https://github.com/cxxr/test-git-repo.git',
            '@version', None, '--depth=3 --origin=github'))

    dest = os.path.join(tmpdir, 'dest-dir')

    finalfile = ext_git(abs_source, dest, {'version':'a057eb0faaa8'}, get_loader(), {})

    assert os.path.exists(finalfile)
    assert os.path.exists(os.path.join(finalfile, '.git'))

    # make sure that --origin=github was applied
    with open(os.path.join(finalfile, '.git', 'config')) as cfile:
        assert 'remote "github"' in cfile.read()

    install_file = os.path.join(finalfile, 'install')
    assert os.path.exists(install_file)

    with open(install_file) as ifile:
        assert ifile.read().strip() == 'echo "Success"'

@pytest.mark.timeout(10)
@pytest.mark.parametrize("ssh_command", [None, "fake_ssh_command"])
def test_sshkey(tmpdir,ssh_command):
    tmpdir = str(tmpdir)

    test_path = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(test_path, 'private_key')) as k:
        private_key = k.read()

    abs_source = os.path.join(tmpdir, 'deploy~git')
    dest = os.path.join(tmpdir, 'dest-dir')

    # Patch check_call so we don't actually call git
    with mock.patch('subprocess.check_call') as submock:
        # Patch git.Repo as there's no git repository made
        with mock.patch('git.Repo') as gitmock:
            # We need a side effect to see if the env variable is being set
            def check_environ(*args):
                if ssh_command:
                    with open(os.environ['GIT_SSH']) as gitfile:
                        if ssh_command not in gitfile.read():
                            assert False

            # Apply the side effect
            submock.check_call.side_effect = check_environ

            # Since this is mocked, it won't actually be hit
            url = 'git@example.org:squadron/test-repo.git'
            version = 'a057eb0faaa8'
            with open(abs_source, 'w') as gfile:
                gfile.write(get_git_file(url, '@version', 'filename', '--depth=1'))

            dest = os.path.join(tmpdir, 'dest-dir2')

            # If we have a special ssh_command to use, use it
            if ssh_command:
                os.environ['GIT_SSH'] = ssh_command

            finalfile = ext_git(abs_source, dest, {'version':version}, get_loader(),
                    {'filename': lambda: private_key})

            # This is the exact command we expect to subprocess
            expected_sub_calls = [mock.call('git clone --depth=1 -- {} {} '.format(url, finalfile).split())]
            # First we make the git.Repo on the destination file, and then we
            # call checkout on the specific version provided
            expected_git_calls = [mock.call(finalfile), mock.call().git.checkout(version)]

            assert expected_sub_calls == submock.mock_calls
            assert expected_git_calls == gitmock.mock_calls

            # Make sure the environment was set up properly
            if ssh_command:
                assert 'GIT_SSH' in os.environ
                assert os.environ['GIT_SSH'] == ssh_command
            else:
                assert 'GIT_SSH' not in os.environ
