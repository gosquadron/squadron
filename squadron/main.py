import os
import commit
import service
import runinfo
from fileio.walkhash import walk_hash, hash_diff
from fileio.config import parse_config, config_defaults
import shutil
import status
import traceback
from log import log
from exceptions import TestException
import tests

def strip_prefix(paths, prefix):
    return [x[len(prefix)+1:] for x in paths]

def get_last_run_info(squadron_state_dir):
    """
    Gets the information from the last run of Squadron.

    Keyword arguments:
        squadron_state_dir -- where Squadron should store its state between runs
    """
    last_run = runinfo.get_last_run_info(squadron_state_dir)

    if 'dir' in last_run:
        last_run_dir = last_run['dir']
        last_run_sum = walk_hash(last_run_dir)
    else:
        last_run_dir = None
        last_run_sum = {}
    return (last_run_dir, last_run_sum)

def go(squadron_dir, squadron_state_dir = None, config_file = None, node_name = None, status_server = None, dry_run = True):
    """
    Gets the config and applies it if it's not a dry run.

    Keyword arguments:
        squadron_dir -- where the Squadron description dir is
        squadron_state_dir -- where Squadron should store its state between runs
        config_file -- overall config file location
        node_name -- what this node is called
        status_server -- the hostname (and optionally port) of the HTTPS server to
            send status to
        dry_run -- whether or not to apply changes
    """
    config = parse_config(config_file)
    log.info("Got config {}".format(config))

    if squadron_state_dir is None:
        squadron_state_dir = config['statedir']
    if node_name is None:
        node_name = config['nodename']

    send_status = False
    if config['send_status'].lower() == 'true':
        send_status = True

        if status_server is None:
            status_server = config['status_host']

        status_apikey = config['status_apikey']
        status_secret = config['status_secret']
        log.info("Sending status to {} with {}/{}".format(status_server, status_apikey, status_secret))

    try:
        _run_squadron(squadron_dir, squadron_state_dir, node_name, dry_run)
    except Exception as e:
        if send_status and not dry_run:
            status.report_status(status_server, status_apikey, status_secret, True, status='ERROR', hostname=node_name, info={'info':True, 'message':str(e)})
        log.exception('Caught exception')
        raise e
    else:
        if send_status and not dry_run:
            status.report_status(status_server, status_apikey, status_secret, True, status='OK', hostname=node_name, info={'info':True})

def _run_squadron(squadron_dir, squadron_state_dir, node_name, dry_run):
    """
    Runs apply to set up the temp directory, and then runs commit if
    dry_run is false.

    Keyword arguments:
        squadron_dir -- where the Squadron description dir is
        squadron_state_dir -- where Squadron should store its state between runs
        node_name -- what this node is called
        dry_run -- whether or not to apply changes
    """
    (last_run_dir, last_run_sum) = get_last_run_info(squadron_state_dir)

    (result, new_dir) = commit.apply(squadron_dir, node_name, dry_run)

    if not new_dir:
        log.error("Error getting changes")
        return False

    this_run_sum = walk_hash(new_dir)

    if this_run_sum != last_run_sum:
        paths_changed, new_paths = hash_diff(last_run_sum, this_run_sum)

        # Remove the temp directory from the front
        paths_changed = strip_prefix(paths_changed, new_dir)
        new_paths = strip_prefix(new_paths, new_dir)

        if not dry_run:
            log.info("Applying changes")
            files_commited = commit.commit(result)

            actions = {}
            reactions = []
            # Get all available actions and reactions
            for service_name in sorted(result):
                version = result[service_name]['version']
                actions.update(service.get_service_actions(squadron_dir,
                    service_name, version))
                reactions.extend(service.get_reactions(squadron_dir,
                    service_name, version))


            # Then react to the changes
            service.react(actions, reactions, paths_changed, new_paths, new_dir)

            # Now test
            for service_name in sorted(result):
                version = result[service_name]['version']
                print("Getting tests for {}/{}".format(service_name, version))
                print "get_tests({}, {}, {})".format(squadron_dir, service_name, version)
                tests_to_run = tests.get_tests(squadron_dir, service_name, version)
                failed_tests = tests.run_tests(tests_to_run)

                if failed_tests:
                    # TODO revert
                    log.error("Aborting due to %s failed tests (total tests %s)", 
                            len(failed_tests), len(tests_to_run))
                    raise TestException()
        else:
            log.info("Dry run changes:\n\tPaths changed: {}\n\tNew files: {}".format(paths_changed, new_paths))
    else:
        log.info("Nothing changed.")

    log.debug("Writing run info to {}, dir : {}".format(squadron_state_dir, new_dir))
    runinfo.write_run_info(squadron_state_dir, {'dir': new_dir})

    if last_run_dir is not None:
        log.debug("Removing last run dir {}".format(last_run_dir))
        shutil.rmtree(last_run_dir)
