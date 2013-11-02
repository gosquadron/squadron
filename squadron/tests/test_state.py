from .. import state
from tempfile import mktemp
import pytest
import random
import os

def test_basic(tmpdir):
    tmpfile = os.path.join(str(tmpdir),'basic')
    handler = state.StateHandler('statetests')

    num = random.randint(0, 100)
    item = {'tmpfile': tmpfile, 'num' : num}
    failed = handler.apply('test1', [item], True)

    assert len(failed) == 1
    assert failed[0] == item

    failed = handler.apply('test1', [item])

    assert len(failed) == 0

    with open(tmpfile, 'r') as testfile:
        assert str(num) == testfile.read()
