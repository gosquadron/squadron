from squadron import resources, log
from helper import get_test_path
import os

log.setup_log('DEBUG', True)

test_path = os.path.join(get_test_path(), 'resources_tests')

def test_basic():
    squadron_dir = os.path.join(test_path, 'basic')

    result = resources.load_resources(squadron_dir)

    assert len(result) == 3
    assert 'basic.txt' in result
    assert 'basic' in result['basic.txt']()

    assert 'dir/second' in result
    assert 'second' in result['dir/second']()

    assert 'deeper/dir/here.sh' in result
    assert 'here' in result['deeper/dir/here.sh']()

def test_empty():
    squadron_dir = os.path.join(test_path, 'empty')

    result = resources.load_resources(squadron_dir)

    assert len(result) == 0
