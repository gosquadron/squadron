from extutils import get_filename
from template import render
from download import _download_file
import os
import requests
import tarfile
import zipfile
import yaml
import jsonschema
import tempfile
import fnmatch
import shutil

def _extract_tar(source, dest):
    tar = tarfile.open(source)
    tar.extractall(dest)

def _extract_zip(source, dest):
    f = zipfile.ZipFile(source)
    f.extractall(dest)

def _extract_jar(source, dest):
    raise NotImplementedError()

EXTRACTORS = {
    'tar.gz': _extract_tar,
    'tar' : _extract_tar,
    'tar.bz2': _extract_tar,
    'zip': _extract_zip,
    'jar': _extract_jar
}

SCHEMA = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'description': 'Describes the extract extension handler input',
    'type':'object',
    'properties': {
        'url': {
            'description': 'Where to download the tarball/zip/etc from',
            'type':'string'
        },
        'type': {
            'description': 'What type of file this is',
            'enum': EXTRACTORS.keys()
        },
        'username': {
            'description': 'Username to login with BASIC Auth',
            'type':'string'
        },
        'password': {
            'description': 'Password to use with BASIC Auth',
            'type':'string'
        },
        'copy': {
            'description': 'Where to copy files within this file to',
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'from': {
                        'type':'string',
                        'description': 'the from glob match'
                    },
                    'to': {
                        'type':'string',
                        'description':'Relative or abs path to destination.'
                    }
                },
                'required': ['from', 'to']
            }
        },
        'persist': {
            'description': 'whether or not to put this file in the root',
            'type':'boolean'
        }
    },
    'required': ['url']
}

def _copy_files(extract_dest, dest, contents):
    to_copy = {}
    for root, dirs, files in os.walk(extract_dest):
        # Get a relative base path
        base = root[len(extract_dest)+1:]

        for filename in files:
            # Get a relative filename
            rel_path = os.path.join(base, filename)

            for copy_item in contents['copy']:
                if fnmatch.fnmatch(rel_path, copy_item['from']):
                    # If it's a relative file, it's relative to dest
                    if not os.path.isabs(copy_item['to']):
                        copy_dest = os.path.join(dest, copy_item['to'])
                    else:
                        copy_dest = copy_item['to']

                    if os.path.isdir(copy_dest):
                        copy_dest = os.path.join(copy_dest, filename)

                    to_copy[os.path.join(root, filename)] = copy_dest

    # This is done in a separate loop to avoid modifying the walk as
    # we walk
    for sourcefile, destfile in to_copy.items():
        shutil.copyfile(sourcefile, destfile)

def ext_extract(abs_source, dest, inputhash, loader, **kwargs):
    contents = yaml.load(render(abs_source, inputhash, loader))

    jsonschema.validate(contents, SCHEMA)

    url = contents['url']
    local_filename = url.split('/')[-1]

    tmpfile = tempfile.NamedTemporaryFile(prefix=local_filename, suffix='.download', delete=False)
    to_delete = [tmpfile.name]
    try:
        auth = None
        if 'username' in contents and 'password' in contents:
            auth = (contents['username'], contents['password'])
        _download_file(url, tmpfile, auth)

        if 'type' in contents:
            extractor = EXTRACTORS[contents['type']]
        else:
            for k in EXTRACTORS.keys():
                if local_filename.endswith('.' + k):
                    extractor = EXTRACTORS[k]
                    break
            else:
                raise UserException('No extractor found for {}'.format(local_filename))

        if 'persist' in contents and not contents['persist']:
            extract_dest = tempfile.mkdtemp(prefix=local_filename, suffix='.sq')
            to_delete.append(extract_dest)
            persist = False
        else:
            extract_dest = dest
            persist = True

        extractor(tmpfile.name, extract_dest)

        if 'copy' in contents:
            _copy_files(extract_dest, dest, contents)

        if persist:
            finalfile = get_filename(dest)
            return finalfile
        else:
            return None
    finally:
        for f in to_delete:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)

