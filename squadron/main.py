import os
import commit
import service
import runinfo
from fileio.walkhash import walk_hash, hash_diff
from fileio.config import parse_config, config_defaults
import shutil

def strip_prefix(paths, prefix):
    return [x[len(prefix)+1:] for x in paths]

def get_last_run_info(squadron_state_dir):
    last_run = runinfo.get_last_run_info(squadron_state_dir)

    if 'dir' in last_run:
        last_run_dir = last_run['dir']
        last_run_sum = walk_hash(last_run_dir)
    else:
        last_run_dir = None
        last_run_sum = {}
    return (last_run_dir, last_run_sum)

def go(squadron_dir, squadron_state_dir = None, config_file = None, node_name = None, dry_run = True):
    config = parse_config(config_defaults(), config_file)

    if squadron_state_dir is None:
        squadron_state_dir = config['statedir']
    if node_name is None:
        node_name = config['nodename']

    (last_run_dir, last_run_sum) = get_last_run_info(squadron_state_dir)

    (result, new_dir) = commit.apply(squadron_dir, node_name, dry_run)

    this_run_sum = walk_hash(new_dir)

    if this_run_sum != last_run_sum:
        paths_changed, new_paths = hash_diff(last_run_sum, this_run_sum)

        # Remove the temp directory from the front
        paths_changed = strip_prefix(paths_changed, new_dir)
        new_paths = strip_prefix(new_paths, new_dir)

        if not dry_run:
            print "Applying changes"
            files_commited = commit.commit(result)

            actions = {}
            reactions = []
            # Get all available actions and reactions
            for service_name in sorted(result):
                actions.update(service.get_service_actions(
                    squadron_dir, service_name, result[service_name]['version']))
                reactions.extend(service.get_reactions(
                    squadron_dir, service_name, result[service_name]['version']))

            service.react(actions, reactions, paths_changed, new_paths, new_dir)
        else:
            print "Dry run changes:\n\tPaths changed: {}\n\tNew files: {}".format(paths_changed, new_paths)
    else:
        print "Nothing changed."

    print "Writing run info to {}, dir : {}".format(squadron_state_dir, new_dir)
    runinfo.write_run_info(squadron_state_dir, {'dir': new_dir})

    if last_run_dir is not None:
        shutil.rmtree(last_run_dir)
