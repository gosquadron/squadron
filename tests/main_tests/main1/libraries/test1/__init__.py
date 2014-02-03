import os

def schema():
    return {
            'title': 'Test schema',
            'type': 'object',
            'properties' : {
                'tmpfile' : {
                    'type' : 'string'
                },
                'num' : {
                    'type' : 'integer'
                }
            }
        }

def verify(inputhashes):
    failed = []
    for ih in inputhashes:
        if os.path.isfile(ih['tmpfile']):
            with open(ih['tmpfile']) as tmpfile:
                if ih['num'] != int(tmpfile.read()):
                    failed.append(ih)
        else:
            failed.append(ih)
    return failed

def apply(**kwargs):
    inputhashes = kwargs['input_hashes']
    for ih in inputhashes:
        with open(ih['tmpfile'], 'w') as tmpfile:
            tmpfile.write(str(ih['num']))
