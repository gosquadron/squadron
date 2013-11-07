import os
import json
import jsonschema
from jsonschema import Draft4Validator, validators
import tempfile
from template import DirectoryRender
from state import StateHandler
from distutils.dir_util import copy_tree
import shutil

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

def apply(squadron_dir, node_info, dry_run=False):
    """
    This method takes input from the given squadron_dir and configures
    a temporary directory according to that information

    Keyword arguments:
        squadron_dir -- configuration directory for input
        node_info -- dictionary of this node's information
        dry_run -- whether or not to actually create the temp directory
            or change any system-wide configuration via state.json
    """
    conf_dir = os.path.join(squadron_dir, 'config', node_info['env'])

    result = {}

    # handle the state of the system via the library
    library_dir = os.path.join(squadron_dir, 'library')
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
    for service in dir_info:
        # copy the directory
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
                print "{} -> {}".format(srcdir, destdir.rstrip('/'))
                os.symlink(srcdir, destdir.rstrip('/'))
            else:
                # Copy
                copy_tree(srcdir, destdir)

            done_files.add(srcdir)

        # Do the remaining files
        for name in files.difference(done_files):
            src = os.path.join(serv_dir, name)
            dst = os.path.join(base_dir, name)
            if os.path.isdir(src):
                copy_tree(src, dst)
            else:
                shutil.copyfile(src, dst)

