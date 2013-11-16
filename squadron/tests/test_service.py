from ..service import get_service_actions, get_reactions, react, _checkfiles
import glob
import os

def test_get_service_actions():
    actions = get_service_actions('service_tests', 'service1', '1.0.1')
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

    assert 'service1.start' in actions['service1.reload']['not_after']
    assert 'service1.restart' in actions['service1.reload']['not_after']

    assert 'service1.start' in actions['service1.restart']['not_after']

def test_get_reactions():
    reactions = get_reactions('service_tests', 'service1', '1.0.1')

    assert len(reactions) == 3

    start = reactions[0]
    assert 'service1.start' in start['execute']
    assert 'apache2.restart' in start['execute']
    assert len(start['when']['command']) > 0
    assert start['when']['exitcode'] == 0

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

def delete_react_temp():
    """ Delete temporary files for this test """
    tmpfiles = glob.glob('/tmp/service1.test.*')
    for f in tmpfiles:
        os.remove(f)

def test_react_basic():
    delete_react_temp()

    try:
        args = {'service_dir':'service_tests',
                'service_name':'service1',
                'service_ver':'1.0.1'}

        actions = get_service_actions(**args)
        actions.update({'apache2.restart': {
            'commands':['touch /tmp/service1.test.apache2.restart']
        }})
        react(actions, get_reactions(**args), ['conf.d/test', 'mods-enabled/mod'], [])

        assert os.path.exists('/tmp/service1.test.start') == True
        assert os.path.exists('/tmp/service1.test.apache2.restart') == True
        # Don't run reload after starting
        assert os.path.exists('/tmp/service1.test.reload') == False
        # Don't run restart after starting
        assert os.path.exists('/tmp/service1.test.restart') == False
    finally:
        delete_react_temp()

def test_react_precendence():
    delete_react_temp()

    try:
        args = {'service_dir':'service_tests',
                'service_name':'service1',
                'service_ver':'2.0'}

        actions = get_service_actions(**args)
        actions.update({'apache2.restart': {
            'commands':['touch /tmp/service1.test.apache2.restart']
        }})

        paths_changed = ['conf.d/new-virtual-host', 'mods-enabled/new-mod']
        react(actions, get_reactions(**args), paths_changed, [])

        assert os.path.exists('/tmp/service1.test.start') == False
        assert os.path.exists('/tmp/service1.test.apache2.restart') == False
        assert os.path.exists('/tmp/service1.test.reload') == False
        assert os.path.exists('/tmp/service1.test.restart') == True

        delete_react_temp()
        react(actions, get_reactions(**args), paths_changed[:1], [])

        assert os.path.exists('/tmp/service1.test.start') == False
        assert os.path.exists('/tmp/service1.test.apache2.restart') == False
        assert os.path.exists('/tmp/service1.test.reload') == True
        assert os.path.exists('/tmp/service1.test.restart') == False
    finally:
        delete_react_temp()
