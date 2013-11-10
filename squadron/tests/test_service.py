from ..service import get_service_actions, get_reactions

def test_get_service_actions():
    actions = get_service_actions('service_tests', 'service1', '1.0.1')
    print "actions {}".format(actions)

    assert len(actions) == 3
    assert 'service1.start' in actions
    assert 'service1.reload' in actions
    assert 'service1.restart' in actions

    assert len(actions['service1.start']['command']) > 0
    assert len(actions['service1.reload']['command']) > 0
    assert len(actions['service1.restart']['command']) > 0

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
    assert start['when']['exitcode'] == 1

    reload = reactions[1]
    assert 'service1.reload' in reload['execute']
    assert len(reload['when']['files']) > 0

    restart = reactions[2]
    assert 'service1.restart' in restart['execute']
    assert len(restart['when']['files']) > 0
