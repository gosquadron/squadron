from .. import template
from tempfile import mkdtemp
from shutil import rmtree
import pytest
from helper import are_dir_trees_equal

def test_template(tmpdir):
    dirname = str(tmpdir)
    test = template.DirectoryRender('template_tests/test1')
    test.render(dirname, {'name':'user'})

    assert are_dir_trees_equal(dirname, 'template_tests/test1result')

def test_extensions():
    assert template.get_ext('filename.txt') == 'txt'
    assert template.get_ext('filename.txt.gz') == 'gz'
    assert template.get_ext('filename.tar') == 'tar'
    assert template.get_ext('filename.tar.gz') == 'tar.gz'
    assert template.get_ext('filename.tar.bz2') == 'tar.bz2'
    assert template.get_ext('filename') == ''

def test_autotest(tmpdir):
    dirname = str(tmpdir)
    test = template.DirectoryRender('template_tests/test-autotest')
    test.render(dirname, {'name':'user'})

    assert are_dir_trees_equal(dirname, 'template_tests/test-autotest-result')

def test_autotest_fail(tmpdir):
    dirname = str(tmpdir)
    test = template.DirectoryRender('template_tests/test-autotest2')

    with pytest.raises(ValueError) as ex:
        test.render(dirname, {'name':'user'})

    assert ex is not None
