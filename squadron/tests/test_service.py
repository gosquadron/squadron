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
    actions = get_reactions('service_tests', 'service1', '1.0.1')
    print "actions {}".format(actions)
