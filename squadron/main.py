import os
import json
import jsonschema
from jsonschema import Draft4Validator, validators
import tempfile
from template import DirectoryRender
from state import StateHandler
from distutils.dir_util import copy_tree
import shutil
from nodes import get_node_info
from collections import defaultdict

# This will be easy to memoize if need be
def get_service_json(squadron_dir, service_name, service_ver, filename):
    """
    Grabs the named JSON file in a service directory

    Keyword arguments:
        squadron_dir -- base directory
        service_name -- the name of the service
        service_ver -- the version of the service
        filename -- the name of the JSON file without the .json extension
    """
    serv_dir = os.path.join(squadron_dir, 'services', service_name, service_ver)
    with open(os.path.join(serv_dir, filename + '.json'), 'r') as jsonfile:
        return json.loads(jsonfile.read())

def check_node_info(node_info):
    if node_info is None:
        print "Couldn't find any node information for node {}".format(node_name)
        return False

    if 'env' not in node_info:
        print "No environment specified in node_info: {}".format(node_info)
        return False

    if 'services' not in node_info or len(node_info['services']) < 1:
        print "No services configured in node_info: {}".format(node_info)
        return False

    return True

def apply(squadron_dir, node_name, dry_run=False):
    """
    This method takes input from the given squadron_dir and configures
    a temporary directory according to that information

    Keyword arguments:
        squadron_dir -- configuration directory for input
        node_name -- this node's name
        dry_run -- whether or not to actually create the temp directory
            or change any system-wide configuration via state.json
    """
    node_info = get_node_info(os.path.join(squadron_dir, 'nodes'), node_name)

    if not check_node_info(node_info):
        # Return early if there's an error
        return False

    conf_dir = os.path.join(squadron_dir, 'config', node_info['env'])

    result = {}

    # handle the state of the system via the library
    library_dir = os.path.join(squadron_dir, 'libraries')
    state = StateHandler(library_dir)

    for service in node_info['services']:
        with open(os.path.join(conf_dir, service + '.json'), 'r') as cfile:
            configdata = json.loads(cfile.read())
            version = configdata['version']
            base_dir = configdata['base_dir']

            # defaults file is optional
            try:
                cfg = get_service_json(squadron_dir, service, version, 'defaults')
            except IOError:
                cfg = {}
                # TODO warn?
                pass
            cfg.update(configdata['config'])


        # validate each schema
        jsonschema.validate(cfg, get_service_json(squadron_dir, service, version, 'schema'))

        if not dry_run:
            service_dir = os.path.join(squadron_dir, 'services',
                                    service, version, 'root')
            render = DirectoryRender(service_dir)

            tmpdir = tempfile.mkdtemp('.sq')
            atomic = render.render(tmpdir, cfg)

            result[service] = {'base_dir': base_dir, 'dir': tmpdir, 'atomic': atomic}

        statejson = get_service_json(squadron_dir, service, version, 'state')
        for library, items in statejson.items():
            state.apply(library, items, dry_run)


    return result



def commit(dir_info):
    """
    Moves files from the temp directory to the final directory based
    on the input given. Returns list of modified files

    Keyword arguments:
        dir_info -- dictionary of service to dir_info hash
    """
    def walk_file_list(srcdir, resultdir):
        result = []
        for root, dirnames, filenames in os.walk(srcdir):
            for filename in filenames:
                result.append(os.path.join(resultdir, filename))
        return result

    result = defaultdict(list)
    for service in dir_info:
        # copy the directory
        print "Doing service {}".format(service)
        serv_dir = dir_info[service]['dir']
        base_dir = dir_info[service]['base_dir']
        files = set(os.listdir(serv_dir))
        done_files = set()
        for dirname, atomic in dir_info[service]['atomic'].items():
            srcdir = os.path.join(serv_dir, dirname)
            destdir = os.path.join(base_dir, dirname)
            # Delete existing dir
            if atomic:
                shutil.rmtree(destdir, ignore_errors=True)
                os.symlink(srcdir, destdir.rstrip('/'))
            else:
                # Copy
                copy_tree(srcdir, destdir)

            print "Before ATOM: {}".format(result[service])
            result[service].extend(walk_file_list(srcdir, dirname))
            print "After ATOM: {}".format(result[service])

            done_files.add(dirname)

        print "Done_files: {}, files: {}".format(done_files, files)
        # Do the remaining files
        for name in files.difference(done_files):
            src = os.path.join(serv_dir, name)
            dst = os.path.join(base_dir, name)
            print "Before list: {}".format(result[service])
            if os.path.isdir(src):
                copy_tree(src, dst)
                result[service].extend(walk_file_list(src, name))
            else:
                shutil.copyfile(src, dst)
                result[service].append(name)
            print "After list: {}".format(result[service])
    return result

