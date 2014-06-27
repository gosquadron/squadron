from squadron import main
import os
import json
from squadron.fileio.dirio import makedirsp
from helper import are_dir_trees_equal, get_test_path
import shutil
import pytest
import squadron

from squadron import log

log.setup_log('DEBUG', console=True)

def create_blank_infojson(statedir):
    open(os.path.join(statedir,'info.json'),'w+').close()

def remove_lock_file(d, lockfile='.lock'):
    try:
        os.remove(os.path.join(d, lockfile))
    except OSError:
        pass

def teardown_function(function):
    try:
        shutil.rmtree('/tmp/main2test/')
    except:
        pass

test_path = os.path.join(get_test_path(), 'main_tests')

def test_main_basic(tmpdir):
    tmpdir = str(tmpdir)

    squadron_state_dir = os.path.join(tmpdir, 'state')
    makedirsp(squadron_state_dir)
    create_blank_infojson(squadron_state_dir)
    makedirsp('/tmp/applytest1/')

    squadron_dir = os.path.join(test_path, 'main1')

    main.go(squadron_dir, squadron_state_dir,
            os.path.join(test_path, 'main1.config'), 'dev',
            None, False, False, False)

    with open(os.path.join(squadron_state_dir, 'info.json')) as infojson:
        info = json.loads(infojson.read())

    assert 'dir' in info
    assert os.path.isdir(info['dir']) == True

    remove_lock_file(info['dir'])
    assert are_dir_trees_equal(os.path.join(test_path, 'main1result'), info['dir']) == True

    old_dir = info['dir']

    main.go(squadron_dir, squadron_state_dir,
            os.path.join(test_path, 'main1.config'), 'dev',
            None, False, False, False)

    with open(os.path.join(squadron_state_dir, 'info.json')) as infojson:
        info = json.loads(infojson.read())

    assert 'dir' in info
    assert os.path.isdir(info['dir']) == True

    new_dir = info['dir']

    assert old_dir == new_dir
    remove_lock_file(info['dir'])
    assert are_dir_trees_equal(os.path.join(test_path, 'main1result'), info['dir']) == True

def test_main_dryrun(tmpdir):
    tmpdir = str(tmpdir)

    squadron_state_dir = os.path.join(tmpdir, 'state')
    makedirsp(squadron_state_dir)
    create_blank_infojson(squadron_state_dir)

    squadron_dir = os.path.join(test_path, 'main1')

    main.go(squadron_dir, squadron_state_dir,
            os.path.join(test_path, 'main1.config'), 'dev',
            None, False, False, True)

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
    main.go(squadron_dir, squadron_state_dir,
            os.path.join(test_path,'main1.config'), None,
            None, False, False, False)

    with open(os.path.join(squadron_state_dir, 'info.json')) as infojson:
        info = json.loads(infojson.read())

    assert 'dir' in info
    assert os.path.isdir(info['dir']) == True
    remove_lock_file(info['dir'])
    assert are_dir_trees_equal(os.path.join(test_path,'main1result'), info['dir']) == True

def test_config_with_bad_dir(tmpdir):
    tmpdir = str(tmpdir)

    squadron_state_dir = os.path.join(tmpdir, 'state')
    makedirsp(squadron_state_dir)
    create_blank_infojson(squadron_state_dir)

    try:
        main.go(None, squadron_state_dir,
                os.path.join(test_path,'bad_dir.config'), None,
                None, False, False, False)
        assert False == "Should have thrown" # Shouldn't get here
    except OSError as e:
        assert e.filename.startswith('/non/existant/dir')

def test_main_git(tmpdir):
    tmpdir = str(tmpdir)

    squadron_state_dir = os.path.join(tmpdir, 'state')
    makedirsp(squadron_state_dir)
    create_blank_infojson(squadron_state_dir)

    squadron_dir = os.path.join(test_path, 'main2')

    main.go(squadron_dir, squadron_state_dir,
            os.path.join(test_path,'main1.config'), 'dev',
            None, False, False, False)

    with open(os.path.join(squadron_state_dir, 'info.json')) as infojson:
        info = json.loads(infojson.read())

    print "info: {}".format(json.dumps(info))
    assert 'dir' in info
    assert os.path.isdir(info['dir']) == True
    remove_lock_file(info['dir'])
    assert are_dir_trees_equal(os.path.join(test_path,'main2result'), info['dir']) == True


@pytest.mark.parametrize("dry_run,dont_rollback", [
    (True, False),
    (True, True),
    (False, False),
    (False, True)
])
def test_rollback(tmpdir, dry_run, dont_rollback):
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

    if dry_run:
        # Should not raise
        main.go(squadron_dir, tmpdir,
                os.path.join(test_path,'main1.config'), 'dev',
                None, dont_rollback, False, dry_run)
    else:
        # This should raise every time
        for i in range(3):
            with pytest.raises(squadron.exceptions.TestException) as ex:
                makedirsp('/tmp/main2test/')
                main.go(squadron_dir, tmpdir,
                        os.path.join(test_path,'main1.config'), 'dev', None,
                        dont_rollback, False, dry_run)

            assert ex is not None

            with open(os.path.join(tmpdir, 'info.json')) as infojson:
                assert info == json.loads(infojson.read())

            assert 'dir' in info
            assert os.path.isdir(info['dir']) == True
            remove_lock_file(info['dir'])
            assert are_dir_trees_equal(old_dir, info['dir'])
            shutil.rmtree('/tmp/main2test/')

@pytest.mark.parametrize("use_the_force", [
    False,
    True,
])
def test_force(tmpdir, use_the_force):
    tmpdir = str(tmpdir)
    force_test = os.path.join(test_path, 'force1')
    force_dir = os.path.join(tmpdir, 'force')

    shutil.copytree(force_test, force_dir)

    action_file = os.path.join(force_dir, 'services', 'api', '0.0.1', 'actions.json')
    result_file = os.path.join(tmpdir,'result')
    with open(action_file, 'w') as afile:
        afile.write(json.dumps({'test':{
            'commands':['touch {}'.format(result_file)]
        }}))

    squadron_state_dir = os.path.join(tmpdir, 'state')
    makedirsp(squadron_state_dir)
    create_blank_infojson(squadron_state_dir)

    main.go(force_dir, squadron_state_dir,
            os.path.join(test_path, 'main1.config'), 'dev',
            None, False, use_the_force, False)

    assert os.path.exists(result_file)
    os.remove(result_file)

    main.go(force_dir, squadron_state_dir,
            os.path.join(test_path, 'main1.config'), 'dev',
            None, False, use_the_force, False)

    if use_the_force:
        assert os.path.exists(result_file)
    else:
        assert not os.path.exists(result_file)

