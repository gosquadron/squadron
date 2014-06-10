from squadron.service import get_service_actions, get_reactions, react, _checkfiles
import glob
import os
from squadron.fileio.dirio import makedirsp
import shutil
from helper import get_test_path
import pytest

test_path = os.path.join(get_test_path(), 'service_tests')

def test_get_service_actions():
    actions = get_service_actions(test_path, 'service1', '1.0.1', {'TEST':'test'})
    print "actions {}".format(actions)

    assert len(actions) == 3
    assert 'service1.start' in actions
    assert 'service1.reload' in actions
    assert 'service1.restart' in actions

    assert len(actions['service1.start']['commands']) > 0
    assert len(actions['service1.reload']['commands']) > 0
    assert len(actions['service1.restart']['commands']) > 0

    assert len(actions['service1.reload']['not_after']) == 2
    assert len(actions['service1.restart']['not_after']) == 1

    assert 'chdir' in actions['service1.start']

    assert 'service1.start' in actions['service1.reload']['not_after']
    assert 'service1.restart' in actions['service1.reload']['not_after']

    assert 'service1.start' in actions['service1.restart']['not_after']

def test_get_reactions():
    reactions = get_reactions(test_path, 'service1', '1.0.1', {'SERVICE':'apache2'})

    assert len(reactions) == 3

    start = reactions[0]
    assert 'service1.start' in start['execute']
    assert 'apache2.restart' in start['execute']
    assert len(start['when']['command']) > 0
    assert start['when']['exitcode_not'] == 0

    reload = reactions[1]
    assert 'service1.reload' in reload['execute']
    assert len(reload['when']['files']) > 0

    restart = reactions[2]
    assert 'service1.restart' in restart['execute']
    assert len(restart['when']['files']) > 0

def test_checkfiles():
    files = ['a.txt','hello/there.conf']
    assert _checkfiles(['*.conf'], files) == True
    assert _checkfiles(['text*', 'hello/*'], files) == True
    assert _checkfiles(['text*', 'hello'], files) == False
    assert _checkfiles([], files) == False
    assert _checkfiles(['test*'], []) == False

@pytest.mark.parametrize("dirname", [
    "/non/existant/dir",
    "relative/dir"
])
def test_chdir(tmpdir, dirname):
    tmpdir = str(tmpdir)
    service_name = "service1"

    actions = {service_name + ".do it": {
        "command":"never execute this",
        "chdir": dirname
    }}
    reactions = [{
        "execute": [service_name + ".do it"],
        "when" : {
            "always": True
        }
    }]

    with pytest.raises(OSError) as ex:
        react(actions, reactions, [], [], tmpdir, {})

    if os.path.isabs(dirname):
        assert ex.value.filename == dirname
    else:
        assert ex.value.filename == os.path.join(tmpdir, service_name, dirname)

def make_react_tmp():
    makedirsp('/tmp/service1')
    makedirsp('/tmp/apache2')

def delete_react_tmp():
    shutil.rmtree('/tmp/service1', ignore_errors=True)
    shutil.rmtree('/tmp/apache2', ignore_errors=True)

def test_react_basic():
    delete_react_tmp()

    make_react_tmp()
    try:
        args = {'service_dir':test_path,
                'service_name':'service1',
                'service_ver':'1.0.1',
                'config': {'TEST':'test','SERVICE':'apache2'}}

        actions = get_service_actions(**args)
        actions.update({'apache2.restart': {
            'commands':['touch /tmp/service1/test.apache2.restart']
        }})
        react(actions, get_reactions(**args), ['conf.d/test', 'mods-enabled/mod'], [], '/tmp', {})

        assert os.path.exists('/tmp/service1/test.start') == True
        assert os.path.exists('/tmp/service1/test.apache2.restart') == True
        # Don't run reload after starting
        assert os.path.exists('/tmp/service1/test.reload') == False
        # Don't run restart after starting
        assert os.path.exists('/tmp/service1/test.restart') == False
    finally:
        delete_react_tmp()

def test_react_precendence():
    delete_react_tmp()

    make_react_tmp()
    try:
        args = {'service_dir':test_path,
                'service_name':'service1',
                'service_ver':'2.0',
                'config': {}}

        actions = get_service_actions(**args)
        actions.update({'apache2.restart': {
            'commands':['touch /tmp/service1/test.apache2.restart']
        }})

        paths_changed = ['service1/conf.d/new-virtual-host', 'service1/mods-enabled/new-mod']
        react(actions, get_reactions(**args), paths_changed, [], '/tmp', {})

        assert os.path.exists('/tmp/service1/test.start') == False
        assert os.path.exists('/tmp/service1/test.apache2.restart') == False
        assert os.path.exists('/tmp/service1/test.reload') == False
        assert os.path.exists('/tmp/service1/test.restart') == True

        delete_react_tmp()
        make_react_tmp()

        react(actions, get_reactions(**args), paths_changed[:1], [], '/tmp', {})

        assert os.path.exists('/tmp/service1/test.start') == False
        assert os.path.exists('/tmp/service1/test.apache2.restart') == False
        assert os.path.exists('/tmp/service1/test.reload') == True
        assert os.path.exists('/tmp/service1/test.restart') == False
    finally:
        delete_react_tmp()

def test_not_exists():
    reactions = get_reactions(test_path, 'service1', '3.0', {})

    assert len(reactions) == 2

    if reactions[0]['execute'][0] == 'service1.go':
        reaction = reactions[0]
        noreaction = reactions[1]
    else:
        reaction = reactions[1]
        noreaction = reactions[0]

    assert 'service1.go' == reaction['execute'][0]
    not_exists = reaction['when']['not_exist']
    assert len(not_exists) == 1
    assert not_exists[0] == '/non/existant'

    # Raising a ValueError is a cheap way to find out if it actually
    # tried to run the reaction. Since the action list is empty, this will
    # raise
    with pytest.raises(ValueError) as ex:
        react([], [reaction], [], [], '/', {})

    assert ex is not None

    # It won't raise if it's not going to be run
    react([], [noreaction], [], [], '/', {})

def test_resource_react(tmpdir):
    tmpdir = str(tmpdir)
    check_file = os.path.join(tmpdir, 'ran_successfully')
    script = '''#!/bin/sh
    if [ ! -r {} ]; then
        touch {}
    else
        exit 1
    fi
    '''.format(check_file, check_file)

    actions = get_service_actions(test_path, 'resources', '1.0', {})
    reactions = get_reactions(test_path, 'resources', '1.0', {})

    assert len(actions) == 1
    assert len(reactions) == 1
   
    react(actions, reactions, [], [], os.path.join(test_path, 'services'), {'test.sh':lambda:script})

    assert os.path.exists(check_file)
