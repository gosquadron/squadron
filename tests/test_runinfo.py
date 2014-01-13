from squadron.runinfo import get_last_run_info, write_run_info
from squadron.fileio.lock import FileLockException
import random
import os
import pytest
from .test_main import create_blank_infojson

def test_basic(tmpdir):
    tmpdir = str(tmpdir)
    info = {'number': random.randint(0,100)}

    write_run_info(tmpdir, info)

    assert get_last_run_info(tmpdir, False) == info

def test_blank(tmpdir):
    tmpdir = str(tmpdir)
    create_blank_infojson(tmpdir)
    assert get_last_run_info(tmpdir, False) == {}

def test_lock_error(tmpdir):
    tmpdir = str(tmpdir)
    info = {'number': random.randint(0,100)}

    with open(os.path.join(tmpdir, 'info.json.lock'), 'w') as lockfile:
        lockfile.write('locked!')

    with pytest.raises(FileLockException) as ex:
        write_run_info(tmpdir, info, timeout=1)

    assert ex is not None

def test_dryrun(tmpdir):
    tmpdir = str(tmpdir)
    info = {'number': random.randint(0,100)}

    write_run_info(tmpdir, info)

    assert get_last_run_info(tmpdir, True) == info

    with open(os.path.join(tmpdir, 'info.json.lock'), 'w') as lockfile:
        lockfile.write('locked!')

    with pytest.raises(FileLockException) as ex:
        # Will fail if it doesn't throw
        assert get_last_run_info(tmpdir, True) is "fail"

    assert ex is not None
