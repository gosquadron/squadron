import git
import shutil
from extutils import get_filename
from template import render
import os
import tempfile
import stat

SSH_WRAPPER='''#!/bin/sh
{} -i {} $@
'''

def _set_ssh_wrapper(contents):
    global SSH_WRAPPER
    SSH_WRAPPER = contents

def _get_ssh_wrapper():
    return str(SSH_WRAPPER)

def write_temp_file(contents, suffix, executable):
    tmpfile = tempfile.NamedTemporaryFile(suffix=suffix,prefix='squadron',delete=False)
    try:
        tmpfile.write(contents)
        if executable:
            os.fchmod(tmpfile.fileno(), stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        return tmpfile.name
    finally:
        tmpfile.close()

def ext_git(abs_source, dest, inputhash, loader, resources, **kwargs):
    """ Clones a git repository """
    contents = render(abs_source, inputhash, loader).split()

    finalfile = get_filename(dest)
    url = contents[0]
    if len(contents) > 1:
        refspec = contents[1]
        if len(contents) > 2:
            sshkey = contents[2]
        else:
            sshkey = None
    else:
        refspec = None
        sshkey = None

    if sshkey:
        key = resources[sshkey]()
        if 'GIT_SSH' in os.environ:
            git_ssh = os.environ['GIT_SSH']
        else:
            git_ssh = 'ssh'
        
        keyfile = write_temp_file(key, '.key', False)
        wrapper = write_temp_file(SSH_WRAPPER.format(git_ssh, keyfile), '.sh', True)

        old_environ = os.environ.copy()
        try:
            os.environ['GIT_SSH'] = wrapper
            print "Calling {}".format(wrapper)
            repo = git.Repo.clone_from(url, finalfile)
        finally:
            os.environ = old_environ
            os.remove(keyfile)
            os.remove(wrapper)
    else:
        repo = git.Repo.clone_from(url, finalfile)

    if refspec:
        repo.git.checkout(refspec)

    return finalfile
