import os
import json
import jsonschema
import template

def init(squadron_dir):
    os.makedirs(os.path.join(squadron_dir, 'libraries'))
    os.makedirs(os.path.join(squadron_dir, 'config'))
    os.makedirs(os.path.join(squadron_dir, 'services'))
    os.makedirs(os.path.join(squadron_dir, 'nodes'))
    os.makedirs(os.path.join(squadron_dir, 'inputchecks'))

def initService(squadron_dir, service_name):
    os.makedirs(os.path.join(squadron_dir, service_name, 'root'))
    os.makedirs(os.path.join(squadron_dir, service_name, 'tests'))
    os.makedirs(os.path.join(squadron_dir, service_name, 'scripts'))
