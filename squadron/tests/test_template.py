from __future__ import print_function
from .. import template
from ..template import FileConfig, get_config, apply_config
from tempfile import mkdtemp
from shutil import rmtree
import pytest
from helper import are_dir_trees_equal
import os
import stat

def test_template(tmpdir):
    dirname = str(tmpdir)
    test = template.DirectoryRender('template_tests/test1')
    test.render(dirname, {'name':'user'})

    assert are_dir_trees_equal(dirname, 'template_tests/test1result')

def test_template_with_config(tmpdir):
    dirname = str(tmpdir)
    test = template.DirectoryRender('template_tests/test2')
    test.render(dirname, {'name':'user'})

    assert are_dir_trees_equal(dirname, 'template_tests/test2result')

    st_file = os.stat(os.path.join(dirname, 'file'))
    assert stat.S_IMODE(st_file.st_mode) == 0642

    st_test3 = os.stat(os.path.join(dirname, 'test3'))
    assert stat.S_IMODE(st_test3.st_mode) == 0775

    st_test3_file = os.stat(os.path.join(dirname, 'test3', 'hello.txt'))
    assert stat.S_IMODE(st_test3_file.st_mode) == 0775

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

def test_parse_config(tmpdir):
    conf_file = os.path.join(str(tmpdir), 'config.sq')
    with open(conf_file, 'w') as wfile:
        print('conf.d atomic:true', file=wfile)
        print('httpd.conf user:sean group:dudes mode:0644', file=wfile)

    result = template.parse_config(conf_file)

    assert len(result) == 2
    assert result[0].filepath == 'conf.d'
    assert result[0].atomic == True
    assert result[0].user == None
    assert result[0].group == None
    assert result[0].mode == None

    assert result[1].filepath == 'httpd.conf'
    assert result[1].atomic == False
    assert result[1].user == 'sean'
    assert result[1].group == 'dudes'
    assert result[1].mode == '0644'

def test_parse_config_error(tmpdir):
    conf_file = os.path.join(str(tmpdir), 'config.sq')
    with open(conf_file, 'w') as wfile:
        print('conf.d', file=wfile)

    with pytest.raises(ValueError) as ex:
        template.parse_config(conf_file)

    assert ex is not None

    conf_file = os.path.join(str(tmpdir), 'config2.sq')
    with open(conf_file, 'w') as wfile:
        print('conf.d atomic:true mdoe:0000', file=wfile)

    with pytest.raises(ValueError) as ex:
        template.parse_config(conf_file)

    assert ex is not None

def test_get_config():
    config = {'conf.d/' : FileConfig('conf.d/', True, None, None, 0755),
              'conf.d/config' : FileConfig('conf.d/config', False, 'user', 'group', None)}

    assert get_config('conf.d/', config) == config['conf.d/']
    assert get_config('conf.d/config', config) == config['conf.d/config']
    assert get_config('conf.d/non-existant-file', config) == config['conf.d/']
    assert get_config('non-exist', config) == FileConfig('non-exist',
            False, None, None, None)

def test_apply_config(tmpdir):
    tmpdir = str(tmpdir)

    filepath = os.path.join(tmpdir, 'test.txt')
    with open(filepath, 'w') as cfile:
        cfile.write('test')

    apply_config(filepath, FileConfig(filepath, False, None, None, '0777'))
    st = os.stat(filepath)
    assert stat.S_IMODE(st.st_mode) == 0777
