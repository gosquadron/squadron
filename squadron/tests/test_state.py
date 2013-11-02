from .. import state
from tempfile import mktemp
import pytest
import random
import os
import jsonschema

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

def test_schema_validation_error(tmpdir):
    tmpfile = os.path.join(str(tmpdir),'basic')
    handler = state.StateHandler('statetests')

    item = {'tmpfile': tmpfile, 'num' : 'five'}
    with pytest.raises(jsonschema.ValidationError) as ex:
        handler.apply('test1', [item], True)

    assert ex.value.cause is None # make sure it was a validation error
    assert ex.value.validator_value == 'integer'
