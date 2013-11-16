from commit import get_service_json
import jsonschema
import subprocess
import fnmatch
import os
from fileio import dirio

_action_schema = {
    'type': 'object',
    'properties': {
        'commands': {
            'description': 'commands to run',
            'type': 'array',
            'items': {
                'type':'string'
            }
        },
        'not_after': {
            'description': 'don\'t run this after any of these actions',
            'type' : 'array',
            'items': {
                'type': 'string'
            },
            'uniqueItems': True
        }
    },
    'required': ['commands']
}

_reaction_schema = {
    'type':'array',
    'items':{
        'type':'object',
        'properties':{
            'execute':{
                'description':'which action to execute',
                'type':'array',
                'items':{
                    'type':'string'
                },
                'minItems': 1,
                'uniqueItems':True
            },
            'when':{
                'type':'object',
                'properties':{
                    'command':{
                        'description':'command to run, use with exitcode',
                        'type':'string'
                    },
                    'exitcode':{
                        'description':'exit code to match',
                        'type':'integer'
                    },
                    'files':{
                        'description':'if any of these files were created or modified',
                        'type':'array',
                        'items':{
                            'type':'string'
                        }
                    },
                    'files_created':{
                        'description':'if any of these files were created',
                        'type':'array',
                        'items':{
                            'type':'string'
                        }
                    },
                    'files_modified':{
                        'description':'if any of these files were modified',
                        'type':'array',
                        'items':{
                            'type':'string'
                        }
                    },
                    'always':{
                        'description':'run always',
                        'type':'boolean'
                    }
                }
            }
        },
        'required': ['execute', 'when']
    }
}

def get_service_actions(service_dir, service_name, service_ver):
    """
    Gets the actions supported by a service

    Keyword arguments:
        service_dir -- top level service directory
        service_name -- name of service
        service_ver -- service version
    """
    action_desc = get_service_json(service_dir, service_name, service_ver, 'actions')

    result = {}
    for k,v in action_desc.items():
        if '.' in k:
            raise ValueError('Key {} in {} v{} is invalid, no dots allowed'.format(
                k, service_name, service_ver))
        jsonschema.validate(v, _action_schema)

        if 'not_after' in v:
            # Prepend service name and dots to any not_after items
            not_after = []
            for subitem in v['not_after']:
                if '.' not in subitem:
                    not_after.append(service_name + '.' + subitem)
                else:
                    not_after.append(subitem)

            v['not_after'] = not_after

        # Prepend dot for the action name always
        result[service_name + '.' + k] = v

    return result

def _prepend_service_name(service_name, files):
    ret = []
    for f in files:
        if not os.path.isabs(f):
            ret.append(os.path.join(service_name, f))
        else:
            ret.append(f)
    return ret

def get_reactions(service_dir, service_name, service_ver):
    """
    Gets the reaction description from a service.

    Keyword arguments:
        service_dir -- top level service directory
        service_name -- name of service
        service_ver -- service version
    """
    reactions_desc = get_service_json(service_dir, service_name, service_ver, 'react')

    jsonschema.validate(reactions_desc, _reaction_schema)

    for reaction in reactions_desc:
        actions = []
        for action in reaction['execute']:
            if '.' not in action:
                actions.append(service_name + '.' + action)
            else:
                actions.append(action)

        when = reaction['when']

        # Prepend service name if relative path
        if 'files_modified' in when:
            when['files_modified'] = _prepend_service_name(service_name, when['files_modified'])
        if 'files_created' in when:
            when['files_created'] = _prepend_service_name(service_name, when['files_created'])
        if 'files' in when:
            when['files'] = _prepend_service_name(service_name, when['files'])

        reaction['execute'] = actions

    return reactions_desc


def _checkfiles(filepatterns, paths_changed):
    """
    Checks to see if any of the files changed match any of the file
    patterns given. File patterns implicitly start at the root of the
    deployment directory.

    Keyword arguments:
        filepatterns -- list of glob-style patterns
        paths_changed -- list of paths changed, each item is relative to the
            base deployment directory
    """
    print "_checkfiles({}, {})".format(filepatterns, paths_changed)
    for pattern in filepatterns:
        if fnmatch.filter(paths_changed, pattern):
            print "Match on pattern {}".format(pattern)
            return True

    print "no match"
    return False

def _runcommand(command, retcode):
    ret = subprocess.call(command)
    return ret == retcode

def react(actions, reactions, paths_changed, new_files, base_dir):
    """
    Performs actions based on reaction criteria. Each action is only performed
    once, and reactions are handled in order.

    Keyword arguments:
        actions -- map of action names to action descriptions
        reactions -- list of reactions to check for
        paths_changes -- list of files that were updated
        new_files -- list of files that are new this run
    """
    done_actions = set()
    for reaction in reactions:
        run_action = False

        when = reaction['when']

        if 'always' in when and when['always']:
            run_action = True
        elif 'command' in when and _runcommand(when['command'], when['exitcode']):
            run_action = True
        elif 'files' in when and _checkfiles(when['files'], paths_changed + new_files):
            run_action = True
        elif 'files_modified' in when and _checkfiles(when['files_modified'], paths_changed):
            run_action = True
        elif 'files_created' in when and _checkfiles(when['files_created'], new_files):
            run_action = True

        if not run_action:
            print "Not running reaction {}".format(reaction)
            continue

        # Run action
        for action in reaction['execute']:
            print "Running action {} in reaction {}".format(action, reaction)
            if action in actions:
                if action not in done_actions:
                    # Actions must be unique
                    not_after = set()
                    action_item = actions[action]
                    if 'not_after' in action_item:
                        not_after = set(action_item['not_after'])

                    if len(done_actions.intersection(not_after)) == 0:
                        # Let's do this
                        service_name = os.path.splitext(action)[0]

                        # For the commands, put us in the service directory
                        # so that relative commands will work
                        with dirio.SafeChdir(os.path.join(base_dir, service_name)):
                            for command in action_item['commands']:
                                try:
                                    subprocess.check_call(command.split())
                                except subprocess.CalledProcessError as e:
                                    print "Command {} errored with code {}".format(command, e.returncode)
                                    raise e
                        done_actions.add(action)
            else:
                raise ValueError(
                        'Action {} from reaction {} not in action list'.format(
                            action, reaction))


