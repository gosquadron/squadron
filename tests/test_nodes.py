from squadron.nodes import get_node_info, _descend
from helper import get_test_path
import os

test_path = os.path.join(get_test_path(), 'nodes_tests')

def test_descend():
    results = _descend(test_path, 'dev-a1.api.example.com')

    assert len(results) == 4
    assert os.path.join(test_path, '#') in results
    assert os.path.join(test_path, 'dev#') in results
    assert os.path.join(test_path, 'base', '#.example.com') in results
    assert os.path.join(test_path, 'dev#.api.example.com') in results

def test_get_node_info():
    result = get_node_info(test_path, 'dev-a1.api.example.com')
    assert result == {'env':'dev', 'services':['api'], 'top-level-setting':True}

    result = get_node_info(test_path, 'www.example.com')
    assert result == {'top-level-setting':True}

    result = get_node_info(test_path, 'dev-database')
    assert result == {'env':'dev', 'top-level-setting':True}
