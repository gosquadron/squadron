import json
from . import schema, verify, apply
import wrap_apt
from mock import MagicMock
import os

def set_test_hook_if_not_root(hook=True):
    if(os.geteuid() != 0):
        wrap_apt.FAKE_RETURN = hook

def test_schema():
    assert len(schema()) > 0

def test_verify_fail():
    set_test_hook_if_not_root(False)
    inputh = ["idonotexist"]
    assert len(verify(inputh)) != 0

def test_verify():
    inputh = ["git"]
    set_test_hook_if_not_root()
    assert len(verify(inputh)) == 0

def test_apply():
    set_test_hook_if_not_root()
    inputh = ["git"]
    assert len(apply(inputh, "")) == 0

def test_apply_new():
    set_test_hook_if_not_root()
    wrap_apt.uninstall_package("zivot")
    inputh = ["zivot"]
    assert len(apply(inputh, "")) == 0
