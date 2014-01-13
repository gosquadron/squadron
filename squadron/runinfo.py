import json
import os
from fileio.lock import FileLock, FileLockException
import time
from log import log

def _get_lock_files(squadron_state_dir):
    info_file = os.path.join(squadron_state_dir, 'info.json')
    lock_file = os.path.join(squadron_state_dir, 'info.json.lock')

    return (info_file, lock_file)

def get_last_run_info(squadron_state_dir, dry_run):
    def read_file(info_file):
        with open(info_file) as jsoninfo:
            contents = jsoninfo.read()
            if contents:
                return json.loads(contents)
            else:
                # Upon installation, this file will be empty
                # so return no last run info
                return {}
    info_file, lock_file = _get_lock_files(squadron_state_dir)

    if not dry_run:
        with FileLock(info_file, timeout=2):
            return read_file(info_file)
    else:
        counter = 10
        while os.path.exists(lock_file) and counter:
            log.debug("Lock file still exists, waiting")
            counter = counter - 1
            time.sleep(0.1)
        if os.path.exists(lock_file):
            raise FileLockException("Lock file {} still exists".format(lock_file))

        return read_file(info_file)


def write_run_info(squadron_state_dir, info, timeout=5):
    info_file, lock_file = _get_lock_files(squadron_state_dir)

    with FileLock(info_file, lock_file, timeout=timeout):
        with open(info_file, 'w') as jsoninfo:
            jsoninfo.write(json.dumps(info))

