from ..nodes import get_node_info, _descend

def test_descend():
    results = _descend('nodes_tests', 'dev-a1.api.example.com')

    assert len(results) == 4
    assert 'nodes_tests/#' in results
    assert 'nodes_tests/dev#' in results
    assert 'nodes_tests/base/#.example.com' in results
    assert 'nodes_tests/dev#.api.example.com' in results

def test_get_node_info():
    result = get_node_info('nodes_tests', 'dev-a1.api.example.com')
    assert result == {'env':'dev', 'services':['api'], 'top-level-setting':True}

    result = get_node_info('nodes_tests', 'www.example.com')
    assert result == {'top-level-setting':True}

    result = get_node_info('nodes_tests', 'dev-database')
    assert result == {'env':'dev', 'top-level-setting':True}
