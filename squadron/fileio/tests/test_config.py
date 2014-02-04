from ..config import CONFIG_PATHS, parse_config
from ...exceptions import UserException
import pytest

def test_failure():
    CONFIG_PATHS = ['/non/existant/path']

    with pytest.raises(UserException) as ex:
        parse_config()

    assert ex is not None
