import shutil
from squadron.fileio import config as squadron_config
from squadron.exceptions import UserException
from squadron.log import log, setup_log
from ConfigParser import SafeConfigParser
from helper import get_test_path
import os
import pytest

test_path = os.path.join(get_test_path(), 'config_tests')

setup_log('DEBUG', console=True)

def test_no_config(tmpdir):
    tmpdir = str(tmpdir)
    squadron_config.CONFIG_PATHS = []
    with pytest.raises(UserException) as ex:
        squadron_config.parse_config(tmpdir, log)
    assert ex is not None

def diff_dict(a, b):
    intersect = intersect_dict(a,b)
    diff = []
    print "diff dict"
    for item in a.keys():
        if not item in intersect:
            diff.append(item)
    print "diff dict a {}".format(diff)
    for item in b.keys():
        if not item in intersect and not item in diff:
            diff.append(item)
    print "diff dict b {}".format(diff)
    return diff

def intersect_dict(initial, diff):
    intersect = []
    for item in initial.keys():
        if(item in diff and diff[item] == initial[item]):
            intersect.append(item)
    print "intersect({}, {}) = {}".format(initial, diff, intersect)
    return intersect

def create_config(output_file, config_func):
    config_parser = SafeConfigParser()
    config_func(config_parser)
    output_file = open(output_file, 'w')
    config_parser.write(output_file)
    output_file.close()

def create_fake_config(output_file):
    def anon(config):
        for sec in squadron_config.CONFIG_SECTIONS:
            config.add_section(sec)
            config.set(sec, 'fakesetting', 'dog')

    create_config(output_file, anon)

def override_func(config):
    config.add_section('squadron')
    for item in squadron_config.CONFIG_DEFAULTS():
        config.set('squadron', item, 'not-default')

def test_defaults(tmpdir):
    tmpdir = str(tmpdir)
    squadron_config.CONFIG_PATHS = ['/tmp/test_config']
    create_fake_config(squadron_config.CONFIG_PATHS[0])
    result = squadron_config.parse_config(tmpdir, log)
    #We have a fake config file that is parsable, but missing everything
    diff = diff_dict(result, squadron_config.CONFIG_DEFAULTS())
    #There should only be one difference, the fakesetting
    assert(len(diff) == 1)
    assert(diff[0] == 'fakesetting')


def test_overrides(tmpdir):
    tmpdir = str(tmpdir)
    output_file = '/tmp/test_override_config'
    squadron_config.CONFIG_PATHS = [output_file]

    create_config(output_file, override_func)

    result = squadron_config.parse_config(tmpdir, log)

    diff = diff_dict(result, squadron_config.CONFIG_DEFAULTS())
    assert(len(diff) == len(squadron_config.CONFIG_DEFAULTS()))
    assert(len(diff) > 0)

def test_singleton(tmpdir):
    tmpdir = str(tmpdir)
    output_file = '/tmp/test_singleton_config'
    squadron_config.CONFIG_PATHS = [output_file]

    create_config(output_file, override_func)

    result = squadron_config.parse_config(tmpdir, log)
    another_call = squadron_config.parse_config(tmpdir, log)
    diff = diff_dict(result, another_call)
    assert(result == another_call)
    assert(len(diff) == 0)

def test_logging(tmpdir):
    tmpdir = str(tmpdir)
    log_config_template = os.path.join(test_path, 'log.config')
    log_config = os.path.join(tmpdir, 'log.config')
    log_file = os.path.join(tmpdir, 'debug.log')
    rotate_file = os.path.join(tmpdir, 'rotate.log')
    
    # setup config file
    with open(log_config, 'w') as lfile:
        with open(log_config_template) as tfile:
            lfile.write(tfile.read().format(log_file, rotate_file))

    config = squadron_config.parse_log_config(tmpdir, log, log_config)

    debug_str = 'Log debug: %s'.format(tmpdir)
    error_str = 'Log error'

    log.debug(debug_str)
    log.error(error_str)

    assert os.path.exists(log_file)
    assert os.path.exists(rotate_file)
    assert verify_log_content(log_file, debug_str)
    assert verify_log_content(log_file, error_str)
    assert verify_log_content(rotate_file, error_str)

    #Assert that we don't log debug since it wasn't specified
    assert not verify_log_content(rotate_file, debug_str)

def verify_log_content(filename, verification):
    f = open(filename, 'r')
    log_content = f.read()
    return (verification in log_content)

@pytest.mark.parametrize("error_file", os.listdir(os.path.join(test_path, 'error')))
def test_logging_error(tmpdir, error_file):
    tmpdir = str(tmpdir)
    with pytest.raises(UserException) as ex:
        squadron_config.parse_log_config(tmpdir, log,
                os.path.join(test_path, 'error', error_file))
