import os
from log import log
import subprocess

def get_tests(squadron_dir, service_name, service_version):
    """
    Returns a list of all tests in for this service. Each test is given absolute from
    the squadron_dir.

    Keyword arguments:
        squadron_dir -- the base squadron directory
        service_name -- the name of the service to grab the tests from
        service_version -- the version of said service
    """
    def get_all_executable_files(directory):
        result = []
        for f in os.listdir(directory):
            fpath = os.path.join(directory, f)
            if os.path.isdir(fpath):
                subresult = [os.path.join(fpath, x) for x in get_all_executable_files(fpath)]
                result.extend(subresult)
            elif os.access(fpath, os.X_OK):
                result.append(fpath)
        return result

    test_path = os.path.join(squadron_dir, 'services', service_name, service_version, 'tests')
    return [os.path.join(test_path, x) for x in get_all_executable_files(test_path)]

def run_tests(tests):
    """
    Runs all the tests given by directly executing them. If they return
    with a non-zero exit code, it adds them to the dictionary returned.

    Keyword arguments:
        tests -- a list of paths to executable test files
    """
    failed_tests = {}
    for t in tests:
        log.debug("Executing test %s", t)
        retcode = subprocess.call(t)
        if retcode:
            failed_tests[t] = retcode
            log.error("Test %s failed with code %s", t, retcode)

    return failed_tests
