import os
import json

def verify_json(filename):
    """ Checks that a JSON file is valid JSON """
    try:
        with open(filename) as jsonfile:
            json.loads(jsonfile.read())
        return True
    except ValueError:
        return False

def verify_yaml(filename):
    """ Checks that a YAML file is valid YAML """
    try:
        with open(filename) as yamlfile:
            yaml.load(yamlfile.read())
        return True
    except yaml.error.YAMLError:
        return False

testable = {'json':verify_json, 'yml':verify_yaml}
