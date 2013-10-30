from .. import main
import pytest
import jsonschema
from helper import are_dir_trees_equal

def test_basic():
    node = {'services' : ['api'], 'env' : 'dev'}
    results = main.apply('applytests/applytest1', node)

    assert len(results) == 1
    assert are_dir_trees_equal(results['api'], 'applytests/applytest1result')

def test_schema_validation_error():
    node = {'services' : ['api'], 'env' : 'dev'}

    with pytest.raises(jsonschema.ValidationError) as ex:
        main.apply('applytests/applytest1-exception', node)

    assert ex.value.cause is None # make sure it was a validation error
    assert ex.value.validator_value == 'integer'
