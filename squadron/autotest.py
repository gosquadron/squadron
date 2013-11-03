import os
import json


def verify_json(filename):
    try:
        with open(filename) as jsonfile:
            json.loads(jsonfile.read())
        return True
    except ValueError:
        return False

testable = {'json':verify_json}
