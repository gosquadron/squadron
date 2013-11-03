import os
import json
import jsonschema
import template
from template import mkdirp

def init(squadron_dir):
    mkdirp(os.path.join(squadron_dir, '/libraries'))
    mkdirp(os.path.join(squadron_dir, '/config'))
    mkdirp(os.path.join(squadron_dir, '/services'))
    mkdirp(os.path.join(squadron_dir, '/nodes'))
    mkdirp(os.path.join(squadron_dir, '/inputchecks'))

def initService(squadron_dir, service_name):
    mkdirp(os.path.join(squadron_dir, '/', service_name, '/root'))
    mkdirp(os.path.join(squadron_dir, '/', service_name, '/tests'))
    mkdirp(os.path.join(squadron_dir, '/', service_name, '/scripts'))
