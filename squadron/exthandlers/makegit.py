import git
import shutil
from extutils import get_filename
from template import render
import os
import tempfile
import stat
import yaml
import jsonschema
import subprocess

SSH_WRAPPER='''#!/bin/sh
{} -i {} $@
'''

SCHEMA = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'description': 'Describes the git extension handler input',
    'type':'object',
    'properties': {
        'url': {
            'description': 'git repo URL',
            'type': 'string'
        },
        'refspec': {
            'description': 'the branch, tag, or commit hash to checkout after clone',
            'type': 'string'
        },
        'sshkey': {
            'description': 'relative path to the ssh key resource',
            'type': 'string'
        },
        'args': {
            'description': 'other command line arguments to git clone',
            'type': 'string'
        }
    },
    'required': ['url']
}

def write_temp_file(contents, suffix, executable):
    tmpfile = tempfile.NamedTemporaryFile(suffix=suffix,prefix='squadron',delete=False)
    try:
        tmpfile.write(contents)
        if executable:
            os.fchmod(tmpfile.fileno(), stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        return tmpfile.name
    finally:
        tmpfile.close()

def _clone_repo(url, dest, args):
    subprocess.check_call('git clone {} -- {} {}'.format(args, url, dest).split())
    return git.Repo(dest)

def ext_git(abs_source, dest, inputhash, loader, resources, **kwargs):
    """ Clones a git repository """
    contents = yaml.load(render(abs_source, inputhash, loader))
    finalfile = get_filename(dest)

    jsonschema.validate(contents, SCHEMA)
    url = contents['url']

    refspec = None
    sshkey = None
    args = ''

    if 'refspec' in contents:
        refspec = contents['refspec']
    if 'sshkey' in contents:
        sshkey = contents['sshkey']
    if 'args' in contents:
        args = contents['args']

    if sshkey:
        key = resources[sshkey]()
        if 'GIT_SSH' in os.environ:
            git_ssh = os.environ['GIT_SSH']
            reset_to_env = True
        else:
            git_ssh = 'ssh'
            reset_to_env = False

        keyfile = write_temp_file(key, '.key', False)
        wrapper = write_temp_file(SSH_WRAPPER.format(git_ssh, keyfile), '.sh', True)
 
        old_environ = os.environ.copy()
        try:
            os.environ['GIT_SSH'] = wrapper
            repo = _clone_repo(url, finalfile, args)
        finally:
            if reset_to_env:
                os.environ['GIT_SSH'] = git_ssh
            else:
                del os.environ['GIT_SSH']
            os.remove(keyfile)
            os.remove(wrapper)
    else:
        repo = _clone_repo(url, finalfile, args)

    if refspec:
        repo.git.checkout(refspec)

    return finalfile
