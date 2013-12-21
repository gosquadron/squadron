import os
import json
import jsonschema
import template
import subprocess
from git import *
from fileio.dirio import makedirsp
import shutil

def init(squadron_dir, gitrepo, force=False, example=False):
    if os.path.exists(squadron_dir):
        # Check if it's empty-ish
        if len(os.listdir(squadron_dir)) > 0 and not force:
            if gitrepo is not None:
                # Grab the gitrepo name out and use that
                repo_name = gitrepo[gitrepo.rstrip('/').rfind('/'):].lstrip('/')
                if repo_name.endswith('.git'):
                    repo_name = repo_name[:-4]

                squadron_dir = os.path.join(squadron_dir, repo_name)
            else:
                print "Directory already exists and isn't empty."
                print "Please provide a new directory or use -f."
                return False

    if gitrepo is None:
        print "Creating Squadron config in {}".format(squadron_dir)
        makedirsp(squadron_dir)
        makedirsp(os.path.join(squadron_dir, 'libraries'))
        makedirsp(os.path.join(squadron_dir, 'config'))
        makedirsp(os.path.join(squadron_dir, 'services'))
        makedirsp(os.path.join(squadron_dir, 'nodes'))
        repo = Repo.init(squadron_dir) # initialize repo
    else:
        print "Cloning Squadron config from {}".format(gitrepo)
        repo = Repo.clone_from(gitrepo, squadron_dir)

    print "Squadron has been initialized"
    if example is False:
        print "Now, you can initialized your service:"
        print "\tsquadron init --service service_name"
    else:
        init_service(squadron_dir, 'example')
        print "We have init an example service for you, please check out services/example"

    return True



def _go_to_root(fn):
    """
    Decorator which will execute the decorated function at the root
    of the git hierarchy. It returns to the old directory after
    executing the function
    """

    def wrapped(squadron_dir, *args, **kwargs):
        old_cwd = os.getcwd()
        try:
            if squadron_dir == os.getcwd():
                # We might not be at the root
                root_dir = Git(squadron_dir).rev_parse('--show-toplevel')

                os.chdir(root_dir)
                squadron_dir = root_dir
            return fn(squadron_dir, *args, **kwargs)
        finally:
            os.chdir(old_cwd)
    return wrapped

@_go_to_root
def init_service(squadron_dir, service_name, service_ver):
    """ Initializes a service with the given name and version """
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

@_go_to_root
def init_environment(squadron_dir, environment_name, copy_from):
    """ Initializes an environment """
    config_dir = os.path.join(squadron_dir, 'config')

    new_env = os.path.join(config_dir, environment_name)

    if copy_from:
        src = os.path.join(config_dir, copy_from)
        shutil.copytree(src, new_env)
    else:
        makedirsp(new_env)
        service_dir = os.path.join(squadron_dir, 'services')
        # Grab all the directories
        to_make = [ d for d in os.listdir(service_dir)
                    if os.path.isdir(os.path.join(service_dir, d)) ]

        for d in to_make:
            open(os.path.join(new_env, d + '.json'), 'w+').close()

    print "Initialized environment {}{}".format(environment_name,
            " copied from " + copy_from if copy_from else "")
    return True
