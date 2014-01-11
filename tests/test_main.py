from squadron import main
import os
import json
from squadron.fileio.dirio import makedirsp
from helper import are_dir_trees_equal, get_test_path
import shutil

def create_blank_infojson(statedir):
    open(os.path.join(statedir,'info.json'),'w+').close()

def remove_lock_file(d, lockfile='.lock'):
    try:
        os.remove(os.path.join(d, lockfile))
    except OSError:
        pass

test_path = os.path.join(get_test_path(), 'main_tests')

def test_main_basic(tmpdir):
    tmpdir = str(tmpdir)

    squadron_state_dir = os.path.join(tmpdir, 'state')
    makedirsp(squadron_state_dir)
    create_blank_infojson(squadron_state_dir)
    makedirsp('/tmp/applytest1/')

    squadron_dir = os.path.join(test_path, 'main1')

    main.go(squadron_dir, squadron_state_dir, os.path.join(test_path, 'main1.config'), 'dev', None, False)

    with open(os.path.join(squadron_state_dir, 'info.json')) as infojson:
        info = json.loads(infojson.read())

    assert 'dir' in info
    assert os.path.isdir(info['dir']) == True

    remove_lock_file(info['dir'])
    assert are_dir_trees_equal(os.path.join(test_path, 'main1result'), info['dir']) == True

    old_dir = info['dir']

    main.go(squadron_dir, squadron_state_dir, os.path.join(test_path, 'main1.config'), 'dev', None, False)

    with open(os.path.join(squadron_state_dir, 'info.json')) as infojson:
        info = json.loads(infojson.read())

    assert 'dir' in info
    assert os.path.isdir(info['dir']) == True

    new_dir = info['dir']

    assert old_dir != new_dir
    remove_lock_file(info['dir'])
    assert are_dir_trees_equal(os.path.join(test_path, 'main1result'), info['dir']) == True
    shutil.rmtree('/tmp/applytest1/')

def test_main_with_config(tmpdir):
    tmpdir = str(tmpdir)

    squadron_state_dir = os.path.join(tmpdir, 'state')
    makedirsp(squadron_state_dir)
    create_blank_infojson(squadron_state_dir)
    makedirsp('/tmp/applytest1/')

    squadron_dir = os.path.join(test_path, 'main1')

    # Gets the node name from the config file
    main.go(squadron_dir, squadron_state_dir, os.path.join(test_path,'main1.config'), None, None, False)

    with open(os.path.join(squadron_state_dir, 'info.json')) as infojson:
        info = json.loads(infojson.read())

    assert 'dir' in info
    assert os.path.isdir(info['dir']) == True
    remove_lock_file(info['dir'])
    assert are_dir_trees_equal(os.path.join(test_path,'main1result'), info['dir']) == True

def test_main_git(tmpdir):
    tmpdir = str(tmpdir)

    squadron_state_dir = os.path.join(tmpdir, 'state')
    makedirsp(squadron_state_dir)
    create_blank_infojson(squadron_state_dir)

    squadron_dir = os.path.join(test_path, 'main2')

    main.go(squadron_dir, squadron_state_dir, os.path.join(test_path,'main1.config'), 'dev', None, False)

    with open(os.path.join(squadron_state_dir, 'info.json')) as infojson:
        info = json.loads(infojson.read())

    assert 'dir' in info
    assert os.path.isdir(info['dir']) == True
    remove_lock_file(info['dir'])
    assert are_dir_trees_equal(os.path.join(test_path,'main2result'), info['dir']) == True
    shutil.rmtree('/tmp/main2test/')

def test_dont_current():
    prefix = 'test1-'
    tempdir = os.path.join(test_path, 'current')

    assert not main._is_current_last(prefix, tempdir,
            os.path.join(tempdir, 'test1-2'))
    assert main._is_current_last(prefix, tempdir,
            os.path.join(tempdir, 'test1-1'))
