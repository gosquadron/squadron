import os
import json
import jsonschema
import template
import subprocess
from git import *

def init(squadron_dir, skeleton, gitrepro):
    if(os.path.exists(squadron_dir)):
        print "Directory already exists, please provide a new directory"
        exit(1)
        #TODO: Consider adding a FORCE flag if it matters

    os.makedirs(squadron_dir)
    ret = True
    if skeleton == True:
        os.makedirs(os.path.join(squadron_dir, 'libraries'))
        os.makedirs(os.path.join(squadron_dir, 'config'))
        os.makedirs(os.path.join(squadron_dir, 'services'))
        os.makedirs(os.path.join(squadron_dir, 'nodes'))
        os.makedirs(os.path.join(squadron_dir, 'inputchecks'))
        repo = True
    elif gitrepro == None:
        print "Using community repro..."
        repo = Repo.clone_from("git@github.com:guscatalano/squadron-init.git", squadron_dir)
    else:
        print "Using custom repro"
        repo = Repo.clone_from(gitrepro, squadron_dir)

    ret = repo != None
    if ret:
        print "Squadron has been initialized"   
    else:
        print "Squadron init seems to have failed"


def initService(squadron_dir, service_name):
    os.makedirs(os.path.join(squadron_dir, service_name, 'root'))
    os.makedirs(os.path.join(squadron_dir, service_name, 'tests'))
    os.makedirs(os.path.join(squadron_dir, service_name, 'scripts'))
