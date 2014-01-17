from ..walkhash import walk_hash, hash_diff
from ..config import parse_config
import os

test_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fileio_tests')

def test_basic_walkhash():
    walkhash1 = os.path.join(test_path, 'walkhash1')
    result = walk_hash(walkhash1)

    assert result == {
            os.path.join('file1.txt'):'45e3c8923e46f64b4baf68dd127e1871511d74782b1af4109435ebc9b73ad42c',
            os.path.join('hello.alpha'):'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
            os.path.join('dir', 'a.b'):'3028acf5e4c1117ab3d2bfbf5ecffb4d3147c9acb452fb375f27a57acd0bc9b7'
        }

def test_basic_hash_diff():
    old = {
        'dir1/a.txt':'abcdef',
        'dir2/b.txt':'012345',
        'dir2/c.txt':'01x345',
    }

    new_hash = {
        'dir1/a.txt':'abcdef',
        'dir2/b.txt':'012346', # different
        'other.txt':'always'
    }

    paths_changed = ['dir2/b.txt']
    new_paths = ['other.txt']

    assert (paths_changed, new_paths) == hash_diff(old, new_hash)

def test_basic_config(tmpdir):
    test_config = """
[ignored]
not_here:true
[squadron]
test=5
override_this=/var/lib/file
go_for_it=yes
"""

    tmpdir = str(tmpdir)
    config_file = os.path.join(tmpdir,'config')
    with open(config_file, 'w') as cfile:
        cfile.write(test_config)

    defaults = {'override_this':'/tmp','not_present':'false555'}
    result = parse_config(config_file, defaults)
    assert len(result) == 4
    assert 'test' in result
    assert result['test'] == '5'

    assert 'override_this' in result
    assert result['override_this'] != defaults['override_this']

    assert 'go_for_it' in result
    assert result['go_for_it'] == 'yes'

    assert 'not_present' in result
    assert result['not_present'] == 'false555'
