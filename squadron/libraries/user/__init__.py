import os
import subprocess
from string import find
from squadron.initialize import default_schema
import pwd
import grp

def schema():
    """
    """
    schema = default_schema.copy()
    schema.update({'properties': {
            'username': {
                'type':'string'
            },
            'shell': {
                'description':'User\'s command shell',
                'type':'string',
            },
            'realname': {
                'description':'User\'s real name',
                'type':'string',
            },
            'homedir': {
                'description':'User\'s home directory location',
                'type':'string'
            },
            'uid': {
                'description':'Set user\'s ID to this',
                'type':'integer',
                'minimum': 0,
                'maximum': 65535,
            },
            'gid': {
                'description':'Set user\'s primary group ID to this',
                'type':'integer',
                'minimum': 0,
                'maximum': 65535,
            },
            'system': {
                'description':'Whether or not this user is a system user',
                'type':'boolean',
            }
        },
        'required':['username']
    })
    return schema

class VerifyError(Exception):
    pass

def verify(inputhashes, **kwargs):
    """
    Checks if the user specified is present with the exact matching
    configuration provided.
    """
    failed = []
    for user in inputhashes:
        username = user['username']
        try:
            result = pwd.getpwnam(username)
            if 'uid' in user:
                if int(user['uid']) != result.pw_uid:
                    raise VerifyError
            if 'gid' in user:
                if int(user['gid']) != result.pw_gid:
                    raise VerifyError
            if 'shell' in user:
                if user['shell'] != result.pw_shell:
                    raise VerifyError
            if 'realname' in user:
                if user['realname'] != result.pw_gecos:
                    raise VerifyError
            if 'homedir' in user:
                if user['homedir'] != result.pw_dir:
                    raise VerifyError
        except KeyError, VerifyError:
            failed.append(user)

    return failed

def apply(inputhashes, log):
    failed = []
    for user in inputhashes:
        username = user['username']
        try:
            result = pwd.getpwnam(username)
            # Can't modify users that already exist...yet
            failed.append(user)
        except KeyError:
            # this is the normal path
            args = ['useradd']
            if 'system' in user:
                if bool(user['system']):
                    args.append('--system')
            if 'uid' in user:
                args.append('--uid')
                args.append(user['uid'])
            if 'gid' in user:
                args.append('--gid')
                args.append(user['gid'])
            if 'shell' in user:
                args.append('--shell')
                args.append(user['shell'])
            if 'realname' in user:
                args.append('--comment')
                args.append(user['realname'])
            if 'homedir' in user:
                args.append('--home')
                args.append(user['homedir'])

            result = subprocess.call(args)

            if result != 0:
                failed.append(user)

    return failed


