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
from fileio.dirio import makedirsp
import errno
from log import log
from fileio.symlink import force_create_symlink

# This will be easy to memoize if need be
def get_service_json(squadron_dir, service_name, service_ver, filename, empty_on_error=False):
    """
    Grabs the named JSON file in a service directory

    Keyword arguments:
        squadron_dir -- base directory
        service_name -- the name of the service
        service_ver -- the version of the service
        filename -- the name of the JSON file without the .json extension
    """
    try:
        serv_dir = os.path.join(squadron_dir, 'services', service_name, service_ver)
        with open(os.path.join(serv_dir, filename + '.json'), 'r') as jsonfile:
            return json.loads(jsonfile.read())
    except IOError as e:
        if e.errno == errno.ENOENT and empty_on_error:
            return {}
        else:
            raise e

def check_node_info(node_info):
    """
    Parses node_info to find what environment this node is in and what
    services it should run.

    Keyword arguments:
        node_info -- dictionary with 'env' and 'services' keys.
    """
    if node_info is None:
        log.error("Couldn't find any node information for node {}".format(node_name))
        return False

    if 'env' not in node_info:
        log.error("No environment specified in node_info: {}".format(node_info))
        return False

    if 'services' not in node_info or len(node_info['services']) < 1:
        log.error("No services configured in node_info: {}".format(node_info))
        return False

    return True

def apply(squadron_dir, node_name, tempdir, dry_run=False):
    """
    This method takes input from the given squadron_dir and configures
    a temporary directory according to that information

    Keyword arguments:
        squadron_dir -- configuration directory for input
        node_name -- this node's name
        tempdir -- the base temporary directory to use
        dry_run -- whether or not to actually create the temp directory
            or change any system-wide configuration via state.json
    """
    node_info = get_node_info(os.path.join(squadron_dir, 'nodes'), node_name)

    if not check_node_info(node_info):
        # Return early if there's an error
        return (False, None)

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
            cfg = get_service_json(squadron_dir, service, version, 'defaults', True)
            cfg.update(configdata['config'])


        # validate each schema
        schema = get_service_json(squadron_dir, service, version, 'schema', True)
        if schema:
            jsonschema.validate(cfg, schema)

        # Setting the state comes first, since the rest of this might
        # depend on the state of the system (like virtualenv)
        statejson = get_service_json(squadron_dir, service, version, 'state', True)
        for library, items in statejson.items():
            log.info("%s %s via %s",
                    "Would install" if dry_run else "Installing",
                    items,
                    library)
            state.apply(library, items, dry_run)

        if not dry_run:
            service_dir = os.path.join(squadron_dir, 'services',
                                    service, version, 'root')
            render = DirectoryRender(service_dir)

            tmp_serv_dir = os.path.join(tempdir, service)
            makedirsp(tmp_serv_dir)
            atomic = render.render(tmp_serv_dir, cfg)

            result[service] = {
                    'atomic': atomic,
                    'base_dir': base_dir,
                    'config': cfg,
                    'dir': tmp_serv_dir,
                    'version':version,
                }

    return result


ignore_copy = shutil.ignore_patterns('.git')

def _smart_copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            _smart_copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(src).st_mtime - os.stat(dst).st_mtime > 1:
                shutil.copy2(s, d)

def commit(dir_info):
    """
    Moves files from the temp directory to the final directory based
    on the input given. Returns list of all files

    Keyword arguments:
        dir_info -- dictionary of service to dir_info hash
    """
    def walk_file_list(base_dir, srcdir, resultdir, done_files=set()):
        """ Gets files that haven't been seen yet """
        result = []
        if not base_dir.endswith(os.sep):
            # For stripping the slash
            base_dir = base_dir + os.sep

        for root, dirnames, filenames in os.walk(srcdir):
            after_base = root[len(base_dir):] #strip absolute
            if after_base not in done_files:
                for filename in filenames:
                    if os.path.join(after_base, filename) not in done_files:
                        result.append(os.path.join(resultdir, filename))
        return result

    result = defaultdict(list)
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
                if not os.path.islink(destdir):
                    shutil.rmtree(destdir, ignore_errors=True)
                stripped = destdir.rstrip(os.sep)
                makedirsp(os.path.dirname(stripped))
                force_create_symlink(srcdir, stripped)
            else:
                # Copy
                copy_tree(srcdir, destdir)

            result[service].extend(walk_file_list(serv_dir, srcdir, dirname))

            done_files.add(dirname.rstrip(os.sep))

        # Do the remaining files
        for name in files.difference(done_files):
            src = os.path.join(serv_dir, name)
            dst = os.path.join(base_dir, name)
            if os.path.isdir(src):
                print "Copying {} to {} (normbase: {}".format(src, dst,
                        os.path.basename(os.path.normpath(src)))
                if os.path.basename(os.path.normpath(src)) == '.git':
                    continue

                # TODO: Look into how this handles file modes, it's not copying
                # them properly
                _smart_copytree(src, dst, ignore=ignore_copy)
                result[service].extend(walk_file_list(serv_dir, src, name, done_files))
            else:
                # TODO: Look into how this handles file modes, it's not copying
                # them properly
                shutil.copyfile(src, dst)
                result[service].append(name)
    return result

