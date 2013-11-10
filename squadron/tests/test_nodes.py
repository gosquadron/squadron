from ..nodes import get_node_info, _descend

def test_descend():
    results = _descend('nodes_tests', 'dev-a1.api.example.com')

    assert len(results) == 3
    assert 'nodes_tests/dev*' in results
    assert 'nodes_tests/base/*.example.com' in results
    assert 'nodes_tests/dev*.api.example.com' in results

def test_get_node_info():
    result = get_node_info('nodes_tests', 'dev-a1.api.example.com')
    assert result == {'env':'dev', 'services':['api']}

    result = get_node_info('nodes_tests', 'www.example.com')
    assert result == {}

    result = get_node_info('nodes_tests', 'dev-database')
    assert result == {'env':'dev'}
