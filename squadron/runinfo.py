import json
import os
from fileio.lock import FileLock

def _get_lock_files(squadron_state_dir):
    info_file = os.path.join(squadron_state_dir, 'info.json')
    lock_file = os.path.join(squadron_state_dir, 'info.json.lock')

    return (info_file, lock_file)

def get_last_run_info(squadron_state_dir):
    info_file, lock_file = _get_lock_files(squadron_state_dir)

    with FileLock(info_file, timeout=2):
        with open(info_file) as jsoninfo:
            contents = jsoninfo.read()
            if contents:
                return json.loads(contents)
            else:
                # Upon installation, this file will be empty
                # so return no last run info
                return {}

def write_run_info(squadron_state_dir, info, timeout=5):
    info_file, lock_file = _get_lock_files(squadron_state_dir)

    with FileLock(info_file, lock_file, timeout=timeout):
        with open(info_file, 'w') as jsoninfo:
            jsoninfo.write(json.dumps(info))

