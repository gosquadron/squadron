from helper import are_dir_trees_equal
from .. import initialize
import os
import json

def test_basic(tmpdir):
    tmpdir = str(tmpdir)
    assert initialize.init(tmpdir, True, None, force=True)

    items = os.listdir(tmpdir)
    assert len(items) > 0

    assert '.git' in items

def test_service(tmpdir):
    tmpdir = str(tmpdir)
    assert initialize.init(tmpdir, True, None, force=True)
    assert initialize.init_service(tmpdir, 'api', '0.0.1')

    items = os.listdir(os.path.join(tmpdir, 'services', 'api'))

    assert len(items) > 0

def test_environment(tmpdir):
    tmpdir = str(tmpdir)
    assert initialize.init(tmpdir, True, None, force=True)
    assert initialize.init_service(tmpdir, 'api', '0.0.1')

    assert initialize.init_environment(tmpdir, 'dev', None)

    config_dir = os.path.join(tmpdir, 'config')
    items = os.listdir(config_dir)

    assert len(items) == 1
    assert 'dev' in items

    dev_dir = os.path.join(config_dir, 'dev')
    subitems = os.listdir(dev_dir)

    assert len(subitems) == 1
    assert 'api.json' in subitems

    # Try copy from
    with open(os.path.join(dev_dir, 'fake.json'), 'w') as fd:
        fd.write(json.dumps({'testing':True}))

    assert initialize.init_environment(tmpdir, 'staging', 'dev')

    assert are_dir_trees_equal(dev_dir, os.path.join(config_dir, 'staging'))
