import os
import commit
import service
import runinfo
from fileio.walkhash import walk_hash, hash_diff
from fileio.config import parse_config, config_defaults
from fileio.dirio import makedirsp
from fileio.gotoroot import *
import shutil
import status
from log import log
from exceptions import TestException
import tests
import py
import sys
import tempfile

def strip_prefix(paths, prefix):
    return [x[len(prefix)+1:] for x in paths]

@go_to_root
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
    log.debug("Got config {}".format(config))

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

def _is_current_last(prefix, tempdir, last_run_dir):
    """
    This method checks if the current directory in use (last_run_dir) is
    going to be removed (has the lowest number).

    Keyword arguments:
        prefix -- The prefix of the temp directories
        tempdir -- the path to the temp directory
        last_run_dir -- the path to the in use directory
    """

    def parse_num(path):
        """
        parse the number out of a path (if it matches the prefix)

        Borrowed from py.path
        """
        if path.startswith(prefix):
            try:
                return int(path[len(prefix):])
            except ValueError:
                pass

    if not last_run_dir:
        return False

    bn = os.path.basename(os.path.normpath(last_run_dir))
    lastmin = None
    matched = False

    minnum = sys.maxint
    for path in os.listdir(tempdir):
        num = parse_num(path)
        if num is not None:
            if minnum > num:
                minnum = num
                matched = bn == path
    return matched

@go_to_root
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
    try:
        run_info = runinfo.get_last_run_info(squadron_state_dir, dry_run)
        last_run_dir = run_info['dir']
        last_run_sum = run_info['checksum']
        last_commit = run_info['commit']
    except KeyError:
        log.debug("Looks like info.json is empty or malformated")
        last_run_dir = None
        last_run_sum = {}
        last_commit = None

    if not dry_run:
        prefix = 'sq-'
        tempdir = os.path.join(squadron_state_dir, 'tmp')
        makedirsp(tempdir)

        local_tempdir = py.path.local(tempdir)
        if _is_current_last(prefix, tempdir, last_run_dir):
            new_dir = py.path.local.make_numbered_dir(rootdir=local_tempdir, prefix=prefix, keep=0)
        else:
            new_dir = py.path.local.make_numbered_dir(rootdir=local_tempdir, prefix=prefix)
        new_dir = str(new_dir) # we want a str not a LocalPath
    else:
        new_dir = tempfile.mkdtemp(prefix='squadron-')

    log.info("Staging directory: %s", new_dir)
    result = commit.apply(squadron_dir, node_name, new_dir, dry_run)

    # Is this different from the last time we ran?
    this_run_sum = walk_hash(new_dir)

    log.debug("Last run sum: %s", last_run_sum)
    log.debug("This run sum: %s", this_run_sum)

    if this_run_sum != last_run_sum:
        paths_changed, new_paths = hash_diff(last_run_sum, this_run_sum)
        if not dry_run:
            _deploy(squadron_dir, new_dir, last_run_dir, result,
                    this_run_sum, last_run_sum, last_commit)
            info = {'dir': new_dir, 'commit':result, 'checksum': this_run_sum}
            log.debug("Writing run info to %s: %s", squadron_state_dir, info)

            runinfo.write_run_info(squadron_state_dir, info)

            log.info("Successfully deployed to %s", new_dir)
        else:
            log.info("Dry run changes")

        log.info("===============")
        log.info("Paths changed:")
        for path in paths_changed:
            log.info("\t%s", path)
        log.info("\nNew paths:")
        for path in new_paths:
            log.info("\t%s", path)
    else:
        if not dry_run:
            _run_tests(squadron_dir, result)
        log.info("Nothing changed.")


@go_to_root
def _deploy(squadron_dir, new_dir, last_dir, commit_info,
        this_run_sum, last_run_sum, last_commit):
    log.info("Applying changes")
    log.debug("Changes: %s", commit_info)
    commit.commit(commit_info)

    actions = {}
    reactions = []

    commit_keys = sorted(commit_info)
    # Get all available actions and reactions
    for service_name in commit_keys:
        version = commit_info[service_name]['version']
        actions.update(service.get_service_actions(squadron_dir,
            service_name, version))
        reactions.extend(service.get_reactions(squadron_dir,
            service_name, version))

    # Then react to the changes
    log.debug("Reacting to changes: %s actions and %s reactions to run",
            len(actions), len(reactions))

    paths_changed, new_paths = hash_diff(last_run_sum, this_run_sum)

    log.debug("Paths changed: %s", paths_changed)
    log.debug("New paths: %s", new_paths)

    service.react(actions, reactions, paths_changed, new_paths, new_dir)
    # Now test
    try:
        _run_tests(squadron_dir, commit_info)
    except TestException:
        # Roll back
        if last_commit:
            log.error("Rolling back to %s because tests failed", last_commit)
            # Flip around the paths changed and new_paths
            _deploy(squadron_dir, last_dir, None, last_commit, last_run_sum,
                    {}, None)
        raise

@go_to_root
def _run_tests(squadron_dir, commit_info):
    commit_keys = sorted(commit_info)
    for service_name in commit_keys:
        version = commit_info[service_name]['version']
        tests_to_run = tests.get_tests(squadron_dir, service_name, version)

        log.info("Running %s tests for %s v%s", len(tests_to_run),
                service_name, version)
        failed_tests = tests.run_tests(tests_to_run, commit_info[service_name])

        if failed_tests:
            log.error("Failed tests for %s v%s: ", service_name, version)
            for failed_test, exitcode in failed_tests.items():
                log.error("\t%s failed with exitcode %s", failed_test, exitcode)

            log.error("Aborting due to %s failed tests (total tests %s)",
                    len(failed_tests), len(tests_to_run))
            raise TestException()
