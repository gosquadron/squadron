import os
import subprocess
from string import find
from platform import system
import platform
#TODO: Consider using python-apt debian package later

#This is used to return success when either: OS is not compatible or we are not running as root
FAKE_RETURN = False

def compatible():
    if(FAKE_RETURN):
        return False
    os = system()
    if os == 'Linux':
        dist = platform.linux_distribution()
        if(dist[0] == 'Debian' or dist[0] == 'Ubuntu'):
            return True
    return False

def run_command(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out,err

def check_package_is_installed(package):
    if(compatible()):
        failed = []
        out = run_command(['dpkg-query', '-W', package])[0].split()
        if len(out) <= 1:
            return False
        return True
    else:
        return FAKE_RETURN

#TODO: Add a check and return True/False
def uninstall_package(package):
    if(compatible()):
        out = run_command(["apt-get", "--purge", "remove", "-y", package])
        return out
    else:
        return FAKE_RETURN

def install_package(package):
    if(compatible()):
        out = run_command(['apt-get', 'install', '-y', package])
        if(find(out[1], 'Permission denied') != -1):
            return False
        if(find(out[0], ('Setting up ' + package)) != -1 and find(out[0], (package + ' already the newest version')) != -1):
            return False
        return True
    else:
        return FAKE_RETURN
