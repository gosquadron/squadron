from .. import commit
import pytest
import jsonschema
from helper import are_dir_trees_equal
import os
import shutil

from ..dirio import makedirsp

def checkfile(filename, compare):
    with open(filename) as ofile:
        assert compare == ofile.read()

def test_apply_only():
    results = commit.apply('applytests/applytest1', 'node')

    assert len(results) == 1
    assert are_dir_trees_equal(results['api']['dir'], 'applytests/applytest1result')

    checkfile('/tmp/test1.out', '55')
    checkfile('/tmp/test2.out', '0')
    os.remove('/tmp/test1.out')
    os.remove('/tmp/test2.out')
    shutil.rmtree(results['api']['dir'])
    # Don't need to delete base_dir as it hasn't been created yet

def test_apply_commit(tmpdir):
    # Need to delete this first in case of bad test run
    shutil.rmtree('/tmp/applytest2', ignore_errors=True)

    tmpdir = str(tmpdir)
    results = commit.apply('applytests/applytest2', 'node')

    assert len(results) == 1
    assert are_dir_trees_equal(results['api']['dir'], 'applytests/applytest2result')

    makedirsp(results['api']['base_dir'])
    commit.commit(results)

    assert are_dir_trees_equal(results['api']['base_dir'], 'applytests/applytest2result')

    checkfile('/tmp/test1.out', '55')
    checkfile('/tmp/test2.out', '0')
    os.remove('/tmp/test1.out')
    os.remove('/tmp/test2.out')
    shutil.rmtree(results['api']['dir'])
    shutil.rmtree(results['api']['base_dir'])

def test_schema_validation_error():
    with pytest.raises(jsonschema.ValidationError) as ex:
        commit.apply('applytests/applytest1-exception', 'node')

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
