import os, platform
import pytest
from . import schema, verify, apply, set_test_hook

root = {
    'username':'root',
    'uid': 0,
    'gid': 0,
}

non_existant_user = {
    'username':'nonexistantuser333'
}

#Fix verify to work in linux before this
@pytest.mark.skipif(platform.system() != 'Darwin', reason="requires osx")
def test_verify():
    result = verify([root, non_existant_user])
    assert len(result) == 1
    assert result[0] == non_existant_user

def test_apply():
    #If not root
    if(os.geteuid() != 0):
        set_test_hook([]) 
    result = verify([root, non_existant_user])
    apply_result = apply(result, "")
    assert len(apply_result) == 0
