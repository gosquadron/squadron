import urllib
from extutils import get_filename
from template import render
import requests
import yaml
import jsonschema

SCHEMA = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'description': 'Describes the extract extension handler input',
    'type':'object',
    'properties': {
        'url': {
            'description': 'Where to download the tarball/zip/etc from',
            'type':'string'
        },
        'username': {
            'description': 'Username to login with BASIC Auth',
            'type':'string'
        },
        'password': {
            'description': 'Password to use with BASIC Auth',
            'type':'string'
        }
    },
    'required': ['url']
}

def _download_file(url, handle, auth=None):
    r = requests.get(url, auth=auth, stream=True)

    for chunk in r.iter_content(chunk_size=4096):
        if chunk: # filter out keep-alive new chunks
            handle.write(chunk)
    handle.close()

def ext_download(loader, inputhash, abs_source, dest, **kwargs):
    """ Downloads a ~download file"""
    contents = yaml.load(render(abs_source, inputhash, loader))

    jsonschema.validate(contents, SCHEMA)

    finalfile = get_filename(dest)
    handle = open(finalfile, 'w')
    auth = None
    if 'username' in contents and 'password' in contents:
        auth = (contents['username'], contents['password'])
    _download_file(contents['url'], handle, auth)

    return finalfile
