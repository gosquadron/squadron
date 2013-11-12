import os
import json
import jsonschema
import template
import subprocess
from git import *
from dirio import makedirsp
import shutil

def init(squadron_dir, skeleton, gitrepro, force=False, example=False):
    if(os.path.exists(squadron_dir) and not force):
        print "Directory already exists, please provide a new directory"
        return False

    makedirsp(squadron_dir)
    ret = True
    if skeleton == True and gitrepro != None:
        print "Can't do skeleton and gitrepro at the same time"
        return False

    if skeleton == False and gitrepro == None:
        skeleton = True #Probably a silly mistake

    if skeleton == True or gitrepro == None:
        print "Creating skeleton..."
        makedirsp(os.path.join(squadron_dir, 'libraries'))
        makedirsp(os.path.join(squadron_dir, 'config'))
        makedirsp(os.path.join(squadron_dir, 'services'))
        makedirsp(os.path.join(squadron_dir, 'nodes'))
        makedirsp(os.path.join(squadron_dir, 'inputchecks'))
        
    if gitrepro != None:
        repo = Repo.clone_from(gitrepro, squadron_dir)
    
    print "Squadron has been initialized"
    if example != True:
        print "If this is your first time with Squadron, you should init a service by passing --service [name] to the previous command"
    else:
        init_service(squadron_dir, 'example')
        print "We have init an example service for you, please check out services/example"
    return True


def init_service(squadron_dir, service_name):
    makedirsp(os.path.join(squadron_dir, 'services', service_name, 'root'))
    makedirsp(os.path.join(squadron_dir, 'services', service_name, 'tests'))
    makedirsp(os.path.join(squadron_dir, 'services', service_name, 'scripts'))
