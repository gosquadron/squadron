import os
import yaml
import jsonschema
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
from quik import FileLoader
import functools

extensions = ['', '.json', '.yml']

def _get_service_file(squadron_dir, service_name, service_ver, filename, on_error=None, config=None):
    """
    Grabs the named service file in a service directory

    Keyword arguments:
        squadron_dir -- base directory
        service_name -- the name of the service
        service_ver -- the version of the service
        filename -- the name of the service file without the extension
        empty_on_error -- if true, returns an empty dict instead of raising error
        config -- if a dict, uses it to template the file before loading it
    """
    ex = None
    for ext in extensions:
        try:
            serv_dir = os.path.join(squadron_dir, 'services', service_name, service_ver)
            service_file = os.path.join(serv_dir, filename + ext)
            if config:
                loader = FileLoader(squadron_dir)
                template = loader.load_template(service_file)
                return yaml.load(template.render(config, loader=loader))
            else:
                with open(service_file, 'r') as sfile:
                    return yaml.load(sfile.read())
        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                ex = e
            else:
                raise e

    if on_error is not None:
        return on_error
    raise ex

def _get_config(conf_dir, service):
    """
    Gets the service configuration

    Keyword arguments:
        conf_dir -- the location of the configuration directory
        service -- the name of the service
    """
    ex = None
    for ext in extensions:
        try:
            with open(os.path.join(conf_dir, service + ext), 'r') as cfile:
                return yaml.load(cfile.read())
        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                ex = e
            else:
                raise e
    raise ex


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

def _apply_copy(copy_config, previous_run, service, tmp_serv_dir):
    if previous_run:
        source_dir = os.path.join(previous_run, service)
        for copy_item in copy_config:
            if 'path' in copy_item:
                source = os.path.join(source_dir, copy_item['path'])
                dest = os.path.join(tmp_serv_dir, copy_item['path'])
                if os.path.isdir(source):
                    log.debug('Copying directory %s to %s', source, dest)
                    _smart_copytree(source, dest)
                elif os.path.exists(source):
                    log.debug('Copying file %s to %s', source, dest)
                    shutil.copyfile(source, dest)
                else:
                    log.info('Copy file %s does not exist: %s',
                            copy_item['path'], source)

def apply(squadron_dir, node_name, tempdir, resources, previous_run,
        dry_run=False):
    """
    This method takes input from the given squadron_dir and configures
    a temporary directory according to that information

    Keyword arguments:
        squadron_dir -- configuration directory for input
        node_name -- this node's name
        tempdir -- the base temporary directory to use
        previous_run -- the previous successfully applied dir
        dry_run -- whether or not to actually create the temp directory
            or change any system-wide configuration via state file
    """
    log.debug('entering commit.apply %s',
            [squadron_dir, node_name, tempdir, resources, dry_run])
    node_info = get_node_info(os.path.join(squadron_dir, 'nodes'), node_name)

    if not check_node_info(node_info):
        # Return early if there's an error
        log.debug('leaving commit.apply, check_node_info returned error')
        return (False, None)

    log.debug("node_info['env']: " + str(node_info['env']))
    conf_dir = os.path.join(squadron_dir, 'config', node_info['env'])

    result = {}

    # handle the state of the system via the library
    library_dir = os.path.join(squadron_dir, 'libraries')
    state = StateHandler(library_dir)
    for service in node_info['services']:
        # Get config
        configdata = _get_config(conf_dir, service)
        version = configdata['version']
        base_dir = configdata['base_dir']

        get_service_file = functools.partial(_get_service_file, squadron_dir, service, version)

        # defaults file is optional
        cfg = get_service_file('defaults', {})
        cfg.update(configdata['config'])

        # validate each schema
        schema = get_service_file('schema', {})
        if schema:
            jsonschema.validate(cfg, schema)

        # Setting the state comes first, since the rest of this might
        # depend on the state of the system (like virtualenv)
        stateinfo = get_service_file('state', {}, config=cfg)
        for state_item in stateinfo:
            library = state_item['name']
            items = state_item['parameters']

            # Should print these out nicely if they're just strings
            if isinstance(items[0], str) or isinstance(items[0], unicode):
                print_items = ', '.join(items)
            else:
                print_items = items

            log.info("%s %s through %s",
                    "Would process" if dry_run else "Processing",
                    print_items,
                    library)
            state.apply(library, items, dry_run)

        service_dir = os.path.join(squadron_dir, 'services',
                                service, version, 'root')
        render = DirectoryRender(service_dir)

        tmp_serv_dir = os.path.join(tempdir, service)
        makedirsp(tmp_serv_dir)
        # Apply templates
        atomic = render.render(tmp_serv_dir, cfg, resources, dry_run)

        # Copy files from previous runs if applicable
        copy_config = get_service_file('copy', [], config=cfg)
        _apply_copy(copy_config, previous_run, service, tmp_serv_dir)

        result[service] = {
                'atomic': atomic,
                'base_dir': base_dir,
                'config': cfg,
                'dir': tmp_serv_dir,
                'version':version,
            }
    log.debug('leaving commit.apply: ' + str(result))
    return result


ignore_copy = shutil.ignore_patterns('.git')

def _smart_copymode(src, dst):
    stat_info = os.stat(src)
    os.chown(dst, stat_info.st_uid, stat_info.st_gid)

def _smart_copyfile(src, dst):
    shutil.copy2(src, dst)
    _smart_copymode(src, dst)

def _smart_copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)

    _smart_copymode(src, dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            _smart_copytree(s, d, symlinks, ignore)
        else:
            # TODO, this is likely hiding a copy same-file bug
            if not os.path.exists(d) or os.stat(src).st_mtime - os.stat(dst).st_mtime > 1:
                _smart_copyfile(s, d)


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

        log.info("Deploying %s to %s", service, base_dir)

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
                if os.path.basename(os.path.normpath(src)) == '.git':
                    continue

                _smart_copytree(src, dst, ignore=ignore_copy)
                result[service].extend(walk_file_list(serv_dir, src, name, done_files))
            else:
                _smart_copyfile(src, dst)
                result[service].append(name)
    return result

