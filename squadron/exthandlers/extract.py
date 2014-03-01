from extutils import get_filename
from template import render
import os
import requests
import tarfile
import jsonschema
import json
import tempfile

def _extract_tar(source, dest):
    tar = tarfile.open(source)
    tar.extractall(dest)

def _extract_zip(source, dest):
    raise NotImplementedError()

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

def _download_file(url, handle):
    r = requests.get(url, stream=True)

    for chunk in r.iter_content(chunk_size=4096):
        if chunk: # filter out keep-alive new chunks
            handle.write(chunk)
    handle.close()

def ext_extract(abs_source, dest, inputhash, loader, **kwargs):
    contents = json.loads(render(abs_source, inputhash, loader))

    jsonschema.validate(contents, SCHEMA)

    url = contents['url']
    local_filename = url.split('/')[-1]

    tmpfile = tempfile.NamedTemporaryFile(prefix=local_filename, suffix='.download', delete=False)
    to_delete = [tmpfile.name]
    try:
        _download_file(url, tmpfile)

        if 'type' in contents:
            extractor = EXTRACTORS[contents['type']]
        else:
            for k in EXTRACTORS.keys():
                if local_filename.endswith('.' + k):
                    extractor = EXTRACTORS[k]
                    break
            else:
                raise UserException('No extractor found for {}'.format(local_filename))

        if 'persist' in contents and not bool(contents['persist']):
            extract_dest = tempfile.mkdtemp(prefix=local_filename, suffix='.sq')
            to_delete.append(extract_dest)
        else:
            extract_dest = dest

        extractor(tmpfile.name, extract_dest)

    finally:
        for f in to_delete:
            os.remove(f)

    finalfile = get_filename(dest)
    return finalfile
