import os
import subprocess
from string import find

def run_command(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out,err

def schema():
    """
    This returns
    """
    return { 'title': 'apt schema',
            'type': 'string'
            }


def verify(inputhashes):
    """
    """ 
    failed = []
    for package in inputhashes:
        out = run_command(['dpkg-query', '-W', package])[0].split()

        if len(out) <= 1:
            failed.append(package)
    return failed

def apply(inputhashes, dry_run=True):
    failed = []
    for package in inputhashes:
        out = run_command(['apt-get', 'install', '-y', package])
        if(find(out[1], 'Permission denied') != -1):
            failed.append(package) # Install failed because we're not root
        if(find(out[0], ('Setting up ' + package)) != -1 and find(out[0], (package + ' already the newest version')) != -1):
            # Something else happened, we weren't installed and we didn't get installed
            failed.append(package)
    return failed


