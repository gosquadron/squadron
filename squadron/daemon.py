from git import *
import os
import time
import main
from fileio.config import parse_config
from log import setup_log, log
import notify.webhook
import notify.server
import threading
import time

def daemonize(squadron_dir, config_file, polltime, repo, node_name):
    """
    Runs squadron every polltime minutes.

    Keyword arguments:
        squadron_dir -- squadron directory
        config_file -- config file or None for defaults
        polltime -- minutes to sleep in between runs
        repo -- source code for the squadron_dir for updating
        node_name -- override for nodename
        loglevel -- how much to log
    """
    log.debug('entering daemon.daemonize %s',
            [squadron_dir, config_file, polltime, repo])
    parsed_config = parse_config(log, config_file)
    print "Daemon is using loglevel: " + str(log.getEffectiveLevel())
    if not polltime:
        polltime = float(parsed_config['polltime'])
    else:
        polltime = float(polltime)

    squadron_dir = main.get_squadron_dir(squadron_dir, parsed_config)

    if not os.path.exists(squadron_dir):
        log.info('Cloning %s into %s', repo, squadron_dir)
        repo = Repo.clone_from(repo, squadron_dir)
    else:
        repo = Repo(squadron_dir)

    wakeup = threading.Event()
    webhook_thread = None
    if 'webhook' in parsed_config:
        run_webhook = parsed_config['webhook']
        if bool(run_webhook):
            user = parsed_config['webhook_username']
            password = parsed_config['webhook_password']

            app = notify.webhook.WebHookHandler(user, password,
                    lambda x: wakeup.set(), log)

            listen = parsed_config['webhook_listen']
            port = parsed_config['webhook_port']

            webhook_thread, webhook_server = notify.server.get_server(listen,
                    port, app.application)

            log.info('Starting webhook server on %s:%s', listen, port)
            webhook_thread.start()

    while True:
        git = repo.git

        start_time = time.time()
        log.debug("Doing git checkout")
        out = git.checkout('master')
        log.debug('Git checkout returned: %s', out)
        log.debug('Doing git pull --rebase')
        out = git.pull('--rebase')
        log.debug('Git pull returned: %s', out)

        try:
            ret = main.go(squadron_dir, node_name=node_name,
                    config_file=config_file, dry_run=False)
        except e:
            log.exception('Caught top level exception')

        end_time = time.time()

        log.debug('daemon is sleeping: %s', polltime)

        if end_time - start_time < 60:
            # Don't wake up too often
            wakeup.clear()

        if wakeup.wait(polltime):
            log.debug('Woken up early')
            wakeup.clear()

    if webhook_thread:
        log.info('Stopping webhook server')
        webhook_server.stop()
        log.debug('Joining webhook server thread')
        webhook_thread.join()
        log.info('Stopped webhook server')

