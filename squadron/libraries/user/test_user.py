from . import schema, verify, apply
import os, platform
import pytest
import jsonschema

root = {
    'username':'root',
    'uid': 0,
    'gid': 0,
}

non_existant_user = {
    'username':'nonexistantuser333'
}

def test_schema():
    jsonschema.validate(root, schema())
    jsonschema.validate(non_existant_user, schema())

def test_verify():
    result = verify([root, non_existant_user])
    assert len(result) == 1
    assert result[0] == non_existant_user

def integration_test_apply():
    result = verify([root, non_existant_user])
    apply_result = apply(result, "")
    assert len(apply_result) == 0
