import os
import json
import jsonschema
import template
import subprocess
from git import *
from fileio.dirio import makedirsp
import shutil

def init(squadron_dir, skeleton, gitrepo, force=False, example=False):
    if os.path.exists(squadron_dir):
        # Check if it's empty-ish
        if len(os.listdir(squadron_dir)) > 0 and not force:
            print "Directory already exists and isn't empty."
            print "Please provide a new directory or use -f."
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
        print "Now, you can initialized your service:"
        print "\tsquadron init --service service_name"
    else:
        init_service(squadron_dir, 'example')
        print "We have init an example service for you, please check out services/example"

    return True


def init_service(squadron_dir, service_name, service_ver):
    """ Initializes a service with the given name and version """
    try:
        if squadron_dir == os.getcwd():
            # We might not be at the root
            old_cwd = os.getcwd()
            root_dir = Git(squadron_dir).rev_parse('--show-toplevel')

            os.chdir(root_dir)
            squadron_dir = root_dir

        service_dir = os.path.join(squadron_dir, 'services', service_name,
                        service_ver)

        makedirsp(os.path.join(service_dir, 'root'))

        # Create the base files
        open(os.path.join(service_dir, 'actions.json'), 'w+').close()
        open(os.path.join(service_dir, 'defaults.json'), 'w+').close()
        open(os.path.join(service_dir, 'react.json'), 'w+').close()
        open(os.path.join(service_dir, 'schema.json'), 'w+').close()
        open(os.path.join(service_dir, 'state.json'), 'w+').close()

        print "Initialized service {} version {}".format(service_name,
                service_ver)

        return True
    finally:
        if old_cwd:
            os.chdir(old_cwd)
