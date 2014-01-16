from squadron import main
import os
import json
from squadron.fileio.dirio import makedirsp
from helper import are_dir_trees_equal, get_test_path
import shutil
import pytest
import squadron

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

def test_main_dryrun(tmpdir):
    tmpdir = str(tmpdir)

    squadron_state_dir = os.path.join(tmpdir, 'state')
    makedirsp(squadron_state_dir)
    create_blank_infojson(squadron_state_dir)

    squadron_dir = os.path.join(test_path, 'main1')

    main.go(squadron_dir, squadron_state_dir, os.path.join(test_path, 'main1.config'), 'dev', None, True)

    with open(os.path.join(squadron_state_dir, 'info.json')) as infojson:
        assert "" == infojson.read()

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

    print "info: {}".format(json.dumps(info))
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

def test_rollback(tmpdir):
    tmpdir = str(tmpdir)
    rollback_test = os.path.join(test_path, 'rollback1')

    old_dir = os.path.join(rollback_test,'temp','sq-59','old_result')
    # Make the real info.json
    with open(os.path.join(rollback_test, 'state', 'info.json.input')) as inputjson:
        with open(os.path.join(tmpdir, 'info.json'), 'w+') as outputjson:
            info = json.loads(inputjson.read())
            info['dir'] = old_dir
            info['commit']['gitolite']['dir'] = os.path.join(info['dir'], info['commit']['gitolite']['dir'])

            for k,v in info['checksum'].items():
                del info['checksum'][k]
                info['checksum'][os.path.join(info['dir'], k)] = v

            outputjson.write(json.dumps(info))

    # Now let's get back to testing
    squadron_dir = os.path.join(rollback_test, 'squadron_dir')

    with pytest.raises(squadron.exceptions.TestException) as ex:
        makedirsp('/tmp/main2test/')
        main.go(squadron_dir, tmpdir, os.path.join(test_path,'main1.config'), 'dev', None, False)

    assert ex is not None

    with open(os.path.join(tmpdir, 'info.json')) as infojson:
        assert info == json.loads(infojson.read())

    assert 'dir' in info
    assert os.path.isdir(info['dir']) == True
    remove_lock_file(info['dir'])
    assert are_dir_trees_equal(old_dir, info['dir'])
    shutil.rmtree('/tmp/main2test/')
