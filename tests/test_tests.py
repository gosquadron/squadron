from squadron import tests
from helper import get_test_path
import os

test_path = os.path.join(get_test_path(), 'tests_test')

def test_recurse_executable():
    result = tests.get_tests('', '', test_path)

    assert len(result) == 3
    assert os.path.join(test_path, 'tests', 'test.sh') in result
    assert os.path.join(test_path, 'tests', 'deep','folder','test.sh') in result
    assert os.path.join(test_path, 'tests', 'deep','anothertest') in result

def test_execute_tests():
    prepend_test = lambda xl: [os.path.join(test_path, 'tests', x) for x in xl]
    successful_tests = prepend_test(['test.sh', os.path.join('deep','anothertest')])
    failure_tests = prepend_test([os.path.join('deep','folder','test.sh')])

    failed_tests = tests.run_tests(successful_tests)

    assert len(failed_tests) == 0

    failed_tests = tests.run_tests(failure_tests)
    
    assert len(failure_tests) == 1
    assert failure_tests[0] in failed_tests
    assert failed_tests[failure_tests[0]] == 1

