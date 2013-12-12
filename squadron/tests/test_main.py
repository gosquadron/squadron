from .. import main
import os
import json
from ..fileio.dirio import makedirsp
from helper import are_dir_trees_equal
import shutil

def test_main_basic(tmpdir):
    tmpdir = str(tmpdir)

    squadron_state_dir = os.path.join(tmpdir, 'state')
    makedirsp(squadron_state_dir)
    makedirsp('/tmp/applytest1/')

    squadron_dir = 'main_tests/main1'

    main.go(squadron_dir, squadron_state_dir, 'main_tests/main1.config', 'dev', None, False)

    with open(os.path.join(squadron_state_dir, 'info.json')) as infojson:
        info = json.loads(infojson.read())

    assert 'dir' in info
    assert os.path.isdir(info['dir']) == True
    assert are_dir_trees_equal('main_tests/main1result', info['dir']) == True

    old_dir = info['dir']

    main.go(squadron_dir, squadron_state_dir, 'main_tests/main1.config', 'dev', None, False)

    with open(os.path.join(squadron_state_dir, 'info.json')) as infojson:
        info = json.loads(infojson.read())

    assert 'dir' in info
    assert os.path.isdir(info['dir']) == True

    new_dir = info['dir']

    assert old_dir != new_dir
    assert are_dir_trees_equal('main_tests/main1result', info['dir']) == True
    shutil.rmtree('/tmp/applytest1/')

def test_main_with_config(tmpdir):
    tmpdir = str(tmpdir)

    squadron_state_dir = os.path.join(tmpdir, 'state')
    makedirsp(squadron_state_dir)
    makedirsp('/tmp/applytest1/')

    squadron_dir = 'main_tests/main1'

    # Gets the node name from the config file
    main.go(squadron_dir, squadron_state_dir, 'main_tests/main1.config', None, None, False)

    with open(os.path.join(squadron_state_dir, 'info.json')) as infojson:
        info = json.loads(infojson.read())

    assert 'dir' in info
    assert os.path.isdir(info['dir']) == True
    assert are_dir_trees_equal('main_tests/main1result', info['dir']) == True

def test_main_git(tmpdir):
    tmpdir = str(tmpdir)

    squadron_state_dir = os.path.join(tmpdir, 'state')
    makedirsp(squadron_state_dir)

    squadron_dir = 'main_tests/main2'

    main.go(squadron_dir, squadron_state_dir, 'main_tests/main1.config', 'dev', None, False)

    with open(os.path.join(squadron_state_dir, 'info.json')) as infojson:
        info = json.loads(infojson.read())

    assert 'dir' in info
    assert os.path.isdir(info['dir']) == True
    assert are_dir_trees_equal('main_tests/main2result', info['dir']) == True
    shutil.rmtree('/tmp/main2test/')
