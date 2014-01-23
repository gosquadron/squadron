from . import schema, verify, apply

root = {
    'username':'root',
    'uid': 0,
    'gid': 0,
}

non_existant_user = {
    'username':'nonexistantuser333'
}

def test_verify():
    result = verify([root, non_existant_user])
    assert len(result) == 1
    assert result[0] == non_existant_user

def test_apply():
    result = verify([root, non_existant_user])
    apply_result = apply(result)
    assert len(apply_result) == 0
