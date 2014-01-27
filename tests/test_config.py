import shutil
import pytest
from squadron.fileio import config as squadron_config
from ConfigParser import SafeConfigParser


def test_no_config():
    squadron_config.CONFIG_PATHS = []
    with pytest.raises(Exception) as ex:
        config.parse_config()
    assert ex is not None

def diff_dict(a, b):
    intersect = intersect_dict(a,b)
    diff = []
    for item in a.keys():
        if not item in intersect:
            diff.append(item)
    for item in b.keys():
        if not item in intersect:
            diff.append(item)
    return diff

def intersect_dict(initial, diff):
    intersect = []
    for item in initial.keys():
        if(item in diff and diff[item] == initial[item]):
            intersect.append(item)
    return intersect

def create_fake_config(output_file):
    config = SafeConfigParser()
    for sec in squadron_config.CONFIG_SECTIONS():
        config.add_section(sec)
        config.set(sec, 'fakesetting', 'dog')
    output_file = open(output_file, 'w')
    config.write(output_file)
    output_file.close()

def test_defaults():
    squadron_config.CONFIG_PATHS = ['/tmp/test_config']
    create_fake_config(squadron_config.CONFIG_PATHS[0])
    result = squadron_config.parse_config()
    #We have a fake config file that is parsable, but missing everything
    diff = diff_dict(result, squadron_config.CONFIG_DEFAULTS()) 
    #There should only be one difference, the fakesetting
    assert(len(diff) == 1)
    assert(diff[0] == 'fakesetting')
