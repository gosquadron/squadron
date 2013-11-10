import os
import json
import jsonschema
import template
import subprocess
from git import *
from dirio import makedirsp
import shutil

def init(squadron_dir, skeleton, gitrepro, force=False):
    if(os.path.exists(squadron_dir) and not force):
        print "Directory already exists, please provide a new directory"
        return False

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
        
    if gitrepro != None:
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
