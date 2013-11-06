import os
import json
import jsonschema
import template
import subprocess
from git import *
from dirio import makedirsp

def init(squadron_dir, skeleton, gitrepro):
    makedirsp(squadron_dir)
    ret = True
    if skeleton == True and gitrepro != None:
        print "Can't do skeleton and gitrepro at the same time"
        return False

    if skeleton == True:
        print "Creating skeleton..."
        makedirsp(os.path.join(squadron_dir, 'libraries'))
        makedirsp(os.path.join(squadron_dir, 'config'))
        makedirsp(os.path.join(squadron_dir, 'services'))
        makedirsp(os.path.join(squadron_dir, 'nodes'))
        makedirsp(os.path.join(squadron_dir, 'inputchecks'))
        repo = True
    elif gitrepro == None:
        print "Using community repo..."
        repo = Repo.clone_from("https://github.com/guscatalano/squadron-init.git", squadron_dir)
    else:
        print "Using custom repro"
        repo = Repo.clone_from(gitrepro, squadron_dir)

    if repo != None:
        print "Squadron has been initialized"
        return True
    else:
        print "Squadron init seems to have failed"
        return False


def initService(squadron_dir, service_name):
    makedirsp(os.path.join(squadron_dir, service_name, 'root'))
    makedirsp(os.path.join(squadron_dir, service_name, 'tests'))
    makedirsp(os.path.join(squadron_dir, service_name, 'scripts'))
