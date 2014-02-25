import os
import subprocess
from string import find
from squadron.initialize import default_schema
import grp

def schema():
    """
    The schema for this library
    """
    schema = default_schema.copy()
    schema.update({'properties': {
            'name': {
                'type':'string'
            },
            'gid': {
                'description':'Set groups\'s ID to this',
                'type':'integer',
                'minimum': 0,
                'maximum': 65535,
            },
            'system': {
                'description':'Whether or not this group is a system group',
                'type':'boolean',
            }
        },
        'required':['name']
    })
    return schema

class VerifyError(Exception):
    pass

def verify(inputhashes, **kwargs):
    """
    Checks if the group specified is present with the exact matching
    configuration provided.
    """
    failed = []
    for group in inputhashes:
        name = group['name']
        try:
            result = grp.getgrnam(name)
            if 'gid' in group:
                if int(group['gid']) != result.gr_gid:
                    raise VerifyError
        except KeyError, VerifyError:
            failed.append(group)

    return failed

def apply(inputhashes, log):
    """
    Adds the group to the system. If the group is currently present, it fails
    as we can't yet modify groups.
    """
    failed = []
    for group in inputhashes:
        name = group['name']
        try:
            result = grp.getgrnam(name)
            # Can't modify groups that already exist...yet
            log.error('Group %s already present, can\'t modify', name)
            failed.append(group)
        except KeyError:
            # this is the normal path
            args = ['groupadd']

            if 'system' in group:
                if bool(group['system']):
                    args.append('--system')
            if 'gid' in group:
                args.append('--gid')
                args.append(group['gid'])

            args.append(name)
            result = subprocess.call(args)
            log.debug('groupadd for %s result %s', args, result)

            if result != 0:
                failed.append(group)

    return failed


