from .. import main
import pytest
import jsonschema

def test_basic():
    node = {'services' : ['api'], 'env' : 'dev'}
    main.apply('applytests/applytest1', node)

def test_schema_validation_error():
    node = {'services' : ['api'], 'env' : 'dev'}

    with pytest.raises(jsonschema.ValidationError) as ex:
        main.apply('applytests/applytest1-exception', node)

    assert ex.value.cause is None # make sure it was a validation error
    assert ex.value.validator_value == 'integer'
