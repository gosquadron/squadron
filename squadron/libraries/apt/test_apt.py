import json
from . import schema, verify, apply, run_command

def test_schema():
    assert len(schema()) > 0

def test_verify_fail():
    inputh = ["idonotexist"]
    assert len(verify(inputh)) != 0

def test_verify():
    inputh = ["git"]
    assert len(verify(inputh)) == 0

def test_apply():
    inputh = ["git"]

    assert len(apply(inputh, dry_run=True)) == 0

def test_apply_new():
    out = run_command(["apt-get", "--purge", "remove", "-y", "zivot"])
    print out
    inputh = ["zivot"]
    assert len(apply(inputh, dry_run=True)) == 0
