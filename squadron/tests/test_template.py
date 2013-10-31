from .. import template
from tempfile import mkdtemp
from shutil import rmtree
import pytest
from helper import are_dir_trees_equal

@pytest.fixture
def gettmpdir():
    tmpdir = mkdtemp()
    yield tmpdir
    rmtree(tmpdir)

def test_template(tmpdir):
    dirname = str(tmpdir)
    test = template.DirectoryRender('test1')
    test.render(dirname, {'name':'user'})

    assert are_dir_trees_equal(dirname, 'test1result')

def test_extensions():
    assert template.get_ext('filename.txt') == 'txt'
    assert template.get_ext('filename.txt.gz') == 'gz'
    assert template.get_ext('filename.tar') == 'tar'
    assert template.get_ext('filename.tar.gz') == 'tar.gz'
    assert template.get_ext('filename.tar.bz2') == 'tar.bz2'
    assert template.get_ext('filename') == ''

