import os
from log import log
import subprocess
import json
import time

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

def run_tests(tests, test_input, timeout = 10, waittime = 0.1):
    """
    Runs all the tests given by directly executing them. If they return
    with a non-zero exit code, it adds them to the dictionary returned.

    Keyword arguments:
        tests -- a list of paths to executable test files
        test_input -- dictionary of key value pairs to provide to the test
        timeout -- how many seconds to let the tests run
        waittime -- how many seconds to wait in between test polls
    """
    failed_tests = {}
    for t in tests:
        log.debug("Executing test %s", t)

        p = subprocess.Popen(t, stdin=subprocess.PIPE)

        to_send = json.dumps(test_input)
        log.debug("Sending test_input to test: %s", to_send)

        # Using write here instead of communicate because communicate
        # blocks on reading output
        try:
            p.stdin.write(to_send + os.linesep)

            countdown = int(timeout / waittime)
            while countdown:
                retcode = p.poll()
                
                if retcode is not None:
                    break

                time.sleep(waittime)
                countdown = countdown - 1
            else:
                p.terminate()
                log.warn("Test %s timed out", t)
                p.wait()
                retcode = 'TIMEOUT'
        except IOError as e:
            log.warn("Caught IOError from process: %s", e)
            retcode = e

        if retcode:
            failed_tests[t] = retcode
            log.error("Test %s failed with code %s", t, retcode)

    return failed_tests
