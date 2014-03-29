from squadron import commit
from squadron.fileio.dirio import makedirsp
import pytest
import jsonschema
from helper import are_dir_trees_equal, get_test_path
import os
import shutil
import json

from squadron.fileio.dirio import makedirsp

def checkfile(filename, compare):
    with open(filename) as ofile:
        assert compare == ofile.read()

test_path = os.path.join(get_test_path(), 'applytests')

@pytest.mark.parametrize("source_dir,dest_dir,do_commit,do_copy",[
    ("applytest1","applytest1result",False, False),
    ("applytest2","applytest2result",True, False),
    ("applytest1","applytest1result",False, True),
])
def test_apply(tmpdir, source_dir, dest_dir, do_commit, do_copy):
    tmpdir = str(tmpdir)

    commit_tmp = os.path.join(tmpdir, 'tmp')
    makedirsp(commit_tmp)

    apply_dir = os.path.join(tmpdir, 'apply')
    # apply_dir must not yet exist
    shutil.copytree(os.path.join(test_path, source_dir), apply_dir)

    # Write out config
    state_tmp = os.path.join(tmpdir,'state')
    makedirsp(state_tmp)
    config_dir = os.path.join(apply_dir, 'config', 'dev')
    makedirsp(config_dir)

    config = {
        'version':'0.0.1',
        'config':{
            'state1':os.path.join(state_tmp,'one'),
            'state2':os.path.join(state_tmp,'two'),
            'dbhostname':'example.com'
        },
        'base_dir':os.path.join(tmpdir,'basedir')
    }

    with open(os.path.join(config_dir, 'api.json'), 'w') as cfile:
        cfile.write(json.dumps(config))

    previous_dir = None
    if do_copy:
        previous_dir = os.path.join(tmpdir, 'previous', 'example', 'path')
        makedirsp(previous_dir)
        with open(os.path.join(previous_dir, 'test.txt'), 'w') as copy_file:
            copy_file.write('You did it!\n')

    results = commit.apply(apply_dir, 'node', commit_tmp, {}, previous_dir)

    assert len(results) == 1
    assert are_dir_trees_equal(results['api']['dir'],
            os.path.join(test_path, dest_dir))

    checkfile(config['config']['state1'], '55')
    checkfile(config['config']['state2'], '0')

    if do_commit:
        makedirsp(results['api']['base_dir'])
        commit.commit(results)

def test_schema_validation_error(tmpdir):
    tmpdir = str(tmpdir)
    with pytest.raises(jsonschema.ValidationError) as ex:
        commit.apply(os.path.join(test_path, 'applytest1-exception'),
                'node', tmpdir, {}, None)

    assert ex.value.cause is None # make sure it was a validation error
    assert ex.value.validator_value == 'integer'

def test_commit_basic(tmpdir):
    tmpdir = str(tmpdir)
    base_dir = os.path.join(tmpdir, 'base_dir')
    serv_dir = os.path.join(tmpdir, 'serv_dir')
    atom_yes = 'atomic'
    atom_no = 'atomic-no'
    atom_dir = os.path.join(serv_dir, atom_yes)
    atom_no_dir = os.path.join(serv_dir, atom_no)

    dir_info = {'api': {'base_dir' : base_dir, 'dir' : serv_dir,
        'atomic': {atom_yes : True, atom_no : False}}}

    # Atomic file
    os.makedirs(atom_dir)
    with open(os.path.join(atom_dir, 'atom.txt'), 'w') as wfile:
        wfile.write('atomic update')

    # Non-atomic directory
    os.makedirs(atom_no_dir)
    with open(os.path.join(atom_no_dir, 'atom-no.txt'), 'w') as wfile:
        wfile.write('non-atomic update')

    # Non-atomic file
    with open(os.path.join(serv_dir, 'non-atom.txt'), 'w') as wfile:
        wfile.write('non-atomic update')

    result = commit.commit(dir_info)

    assert are_dir_trees_equal(base_dir, serv_dir)

    assert os.path.islink(os.path.join(base_dir, atom_yes)) == True
    assert os.path.islink(os.path.join(base_dir, atom_no)) == False

    assert len(result) == 1
    assert 'api' in result
    assert len(result['api']) == 3
    assert 'atomic/atom.txt' in result['api']
    assert 'atomic-no/atom-no.txt' in result['api']
    assert 'non-atom.txt' in result['api']

def test_commit_deep(tmpdir):
    tmpdir = str(tmpdir)
    base_dir = os.path.join(tmpdir, 'base_dir')
    serv_dir = os.path.join(tmpdir, 'serv_dir')
    atom_base = 'atomic-no1'
    atom_yes = os.path.join(atom_base, 'atomic')
    atom_no = 'atomic-no2'
    atom_dir = os.path.join(serv_dir, atom_yes)
    atom_base_dir = os.path.join(serv_dir, atom_base)
    atom_no_dir = os.path.join(serv_dir, atom_no)

    dir_info = {'api': {'base_dir' : base_dir, 'dir' : serv_dir,
        'atomic': {atom_yes : True, atom_no : False}}}

    # Atomic file
    os.makedirs(atom_dir)
    with open(os.path.join(atom_dir, 'atom.txt'), 'w') as wfile:
        wfile.write('atomic update')

    with open(os.path.join(atom_base_dir, 'atom-no.txt'), 'w') as wfile:
        wfile.write('not an atomic update')

    # Non-atomic directory
    os.makedirs(atom_no_dir)
    with open(os.path.join(atom_no_dir, 'atom-no.txt'), 'w') as wfile:
        wfile.write('non-atomic update')

    # Non-atomic file
    with open(os.path.join(serv_dir, 'non-atom.txt'), 'w') as wfile:
        wfile.write('non-atomic update')

    result = commit.commit(dir_info)

    assert are_dir_trees_equal(base_dir, serv_dir)

    assert os.path.islink(os.path.join(base_dir, atom_yes)) == True
    assert os.path.islink(os.path.join(base_dir, atom_base)) == False
    assert os.path.islink(os.path.join(base_dir, atom_no)) == False

    assert len(result) == 1
    assert 'api' in result
    assert len(result['api']) == 4
    assert 'atomic-no1/atomic/atom.txt' in result['api']
    assert 'atomic-no1/atom-no.txt' in result['api']
    assert 'atomic-no2/atom-no.txt' in result['api']
    assert 'non-atom.txt' in result['api']
