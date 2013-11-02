import os
import json
import jsonschema
from jsonschema import Draft4Validator, validators
import tempfile
from template import DirectoryRender
from state import StateHandler

# This will be easy to memoize if need be
def get_service_json(squadron_dir, service_name, service_ver, filename):
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
    library_dir = os.path.join(squadron_dir, 'library')
    state = StateHandler(library_dir)
    for service in node_info['services']:
        with open(os.path.join(conf_dir, service + '.json'), 'r') as cfile:
            metadata = json.loads(cfile.read())
            version = metadata['version']

            try:
                cfg = get_service_json(squadron_dir, service, version, 'defaults')
            except IOError:
                cfg = {}
                # TODO warn?
                pass
            cfg.update(metadata['config'])


        jsonschema.validate(cfg, get_service_json(squadron_dir, service, version, 'schema'))

        if not dry_run:
            service_dir = os.path.join(squadron_dir, 'services',
                                    service, version, 'root')
            render = DirectoryRender(service_dir)

            tmpdir = tempfile.mkdtemp('.sq')
            render.render(tmpdir, cfg)

            result[service] = tmpdir

        statejson = get_service_json(squadron_dir, service, version, 'state')
        for library, items in statejson.items():
            state.apply(library, items, dry_run)


    return result

