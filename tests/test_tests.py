from squadron.tests import get_tests, run_tests
from helper import get_test_path
import os

test_path = os.path.join(get_test_path(), 'tests_test')

def test_recurse_executable():
    result = get_tests('', '', test_path)

    assert len(result) == 3
    assert os.path.join(test_path, 'tests', 'test.sh') in result
    assert os.path.join(test_path, 'tests', 'deep','folder','test.sh') in result
    assert os.path.join(test_path, 'tests', 'deep','anothertest') in result

def test_execute_tests():
    prepend_test = lambda xl: [os.path.join(test_path, 'tests', x) for x in xl]
    successful_tests = prepend_test(['test.sh', os.path.join('deep','anothertest')])
    failure_tests = prepend_test([os.path.join('deep','folder','test.sh')])

    failed_tests = run_tests(successful_tests, {})

    assert len(failed_tests) == 0

    failed_tests = run_tests(failure_tests, {})
    
    assert len(failure_tests) == 1
    assert failure_tests[0] in failed_tests
    assert failed_tests[failure_tests[0]] == 1

def test_execute_input():
    input_test = os.path.join(test_path, 'tests', 'test.sh')

    failed_tests = run_tests([input_test], {'fail':False})

    assert len(failed_tests) == 0

    failed_tests = run_tests([input_test], {'fail':True})

    assert len(failed_tests) == 1
    print failed_tests
    assert failed_tests[input_test] == 1

def test_timeout():
    input_test = os.path.join(test_path, 'tests', 'test.sh')

    failed_tests = run_tests([input_test], {'timeout':True}, timeout=0.5)

    assert len(failed_tests) == 1
    assert failed_tests[input_test] == 'TIMEOUT'
