import os
import json
import jsonschema

# This will be easy to memoize if need be
def get_schema(squadron_dir, service_name, service_ver):
    serv_dir = os.path.join(squadron_dir, 'services', service_name, service_ver)
    with open(os.path.join(serv_dir, 'schema.json'), 'r') as schemafile:
        schema = json.loads(schemafile.read())
        return schema

def apply(squadron_dir, node_info):
    conf_dir = os.path.join(squadron_dir, 'config', node_info['env'])

    config = {}
    for service in node_info['services']:
        with open(os.path.join(conf_dir, service + '.json'), 'r') as cfile:
            metadata = json.loads(cfile.read())
            version = metadata['version']
            cfg = metadata['config']

            jsonschema.validate(cfg, get_schema(squadron_dir, service, version))
