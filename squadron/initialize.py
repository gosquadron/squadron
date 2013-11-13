import os
import json
import jsonschema
import template
import subprocess
from git import *
from dirio import makedirsp
import shutil

def init(squadron_dir, skeleton, gitrepo, force=False, example=False):
    if(os.path.exists(squadron_dir) and not force):
        print "Directory already exists, please provide a new directory"
        return False

    makedirsp(squadron_dir)
    if skeleton is True and gitrepo is not None:
        print "Can't do skeleton and gitrepo at the same time"
        return False

    if skeleton is False and gitrepo is None:
        skeleton = True #Probably a silly mistake

    if skeleton is True or gitrepo is None:
        print "Creating skeleton..."
        makedirsp(os.path.join(squadron_dir, 'libraries'))
        makedirsp(os.path.join(squadron_dir, 'config'))
        makedirsp(os.path.join(squadron_dir, 'services'))
        makedirsp(os.path.join(squadron_dir, 'nodes'))

    if gitrepo is not None:
        repo = Repo.clone_from(gitrepo, squadron_dir)
    else:
        repo = Repo.init(squadron_dir) # initialize repo

    print "Squadron has been initialized"
    if example is False:
        print "If this is your first time with Squadron, you should init a service by passing --service [name] to the previous command"
    else:
        init_service(squadron_dir, 'example')
        print "We have init an example service for you, please check out services/example"

    return True


def init_service(squadron_dir, service_name, service_ver='0.0.1'):
    """ Initializes a service with the given name and version """
    makedirsp(os.path.join(squadron_dir, 'services', service_name, service_ver,'root'))
