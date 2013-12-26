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

testable = {'json':verify_json}
