import os
import json
import jsonschema
from jsonschema import Draft4Validator, validators
import tempfile
from template import DirectoryRender

# This will be easy to memoize if need be
def get_service_json(squadron_dir, service_name, service_ver, filename):
    serv_dir = os.path.join(squadron_dir, 'services', service_name, service_ver)
    with open(os.path.join(serv_dir, filename + '.json'), 'r') as jsonfile:
        return json.loads(jsonfile.read())

def apply(squadron_dir, node_info, dry_run=False):
    conf_dir = os.path.join(squadron_dir, 'config', node_info['env'])

    result = {}
    for service in node_info['services']:
        cfg = {}
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

    return result

