from ..runinfo import get_last_run_info, write_run_info
from ..fileio.lock import FileLockException
import random
import os
import pytest

def test_basic(tmpdir):
    tmpdir = str(tmpdir)
    info = {'number': random.randint(0,100)}

    write_run_info(tmpdir, info)

    assert get_last_run_info(tmpdir) == info

def test_lock_error(tmpdir):
    tmpdir = str(tmpdir)
    info = {'number': random.randint(0,100)}

    with open(os.path.join(tmpdir, 'info.json.lock'), 'w') as lockfile:
        lockfile.write('locked!')

    with pytest.raises(FileLockException) as ex:
        write_run_info(tmpdir, info, timeout=1)

    assert ex is not None
