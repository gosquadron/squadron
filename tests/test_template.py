from __future__ import print_function
from squadron import template
from squadron.template import FileConfig, get_config, apply_config
from squadron.exthandlers.extutils import get_filename
from squadron.log import log, setup_log
from tempfile import mkdtemp
from shutil import rmtree
import pytest
from helper import are_dir_trees_equal, get_test_path
import os
import stat

setup_log('DEBUG', console=True)

test_path = os.path.join(get_test_path(), 'template_tests')

def test_template_basic(tmpdir):
    dirname = str(tmpdir)
    test = template.DirectoryRender(os.path.join(test_path, 'test1'))
    test.render(dirname, {'name':'user', 'variable': 'test3'}, {})

    assert are_dir_trees_equal(dirname, os.path.join(test_path, 'test1result'))

def test_template_chown_problem(tmpdir):
    dirname = str(tmpdir)
    test = template.DirectoryRender(os.path.join(test_path, 'test1-notpermitted'))

    with pytest.raises(OSError) as ex:
        test.render(dirname, {'name':'user'}, {}, False)

    test.render(dirname, {'name':'user'}, {}, True)

    assert are_dir_trees_equal(dirname, os.path.join(test_path, 'test1result'))

def test_template_with_config(tmpdir):
    dirname = str(tmpdir)
    test = template.DirectoryRender(os.path.join(test_path,'test2'))
    result = test.render(dirname, {'name':'user'}, {})

    assert are_dir_trees_equal(dirname, os.path.join(test_path,'test2result'))

    assert len(result) == 3
    assert result['test2/'] == True
    assert result['test3/'] == False
    assert result['test3/atomic/'] == True

    st_file = os.stat(os.path.join(dirname, 'file'))
    assert stat.S_IMODE(st_file.st_mode) == 0642

    st_test3 = os.stat(os.path.join(dirname, 'test3'))
    assert stat.S_IMODE(st_test3.st_mode) == 0775

    st_test3_file = os.stat(os.path.join(dirname, 'test3', 'hello.txt'))
    assert stat.S_IMODE(st_test3_file.st_mode) != 0775 # not recursive

def test_template_with_config_dir_error(tmpdir):
    dirname = str(tmpdir)

    with pytest.raises(ValueError) as ex:
        test = template.DirectoryRender(os.path.join(test_path,'config-dir-error'))
        result = test.render(dirname, {'name':'user'}, {})
    assert ex is not None

def test_extensions():
    assert template.get_sq_ext('filename.txt') == ''
    assert template.get_sq_ext('filename.txt~gz') == 'gz'
    assert template.get_sq_ext('filename~tar') == 'tar'
    assert template.get_sq_ext('filename~~~tar.gz') == 'tar.gz'
    assert template.get_sq_ext('filename~tar.bz2') == 'tar.bz2'
    assert template.get_sq_ext('filename') == ''

    assert get_filename('filename.txt') == 'filename.txt'
    assert get_filename('filename.txt~gz') == 'filename.txt'
    assert get_filename('filename~tar') == 'filename'
    assert get_filename('filename~~~tar.gz') == 'filename'
    assert get_filename('filename~tar.bz2') == 'filename'
    assert get_filename('filename') == 'filename'

    assert template.get_file_ext('filename.txt') == 'txt'
    assert template.get_file_ext('filename.txt.gz') == 'gz'
    assert template.get_file_ext('filename.tar') == 'tar'
    assert template.get_file_ext('filename.tar.gz') == 'tar.gz'
    assert template.get_file_ext('filename.tar.bz2') == 'tar.bz2'
    assert template.get_file_ext('filename') == ''


    with pytest.raises(ValueError) as ex:
        get_filename('~tpl')
    assert ex is not None

def test_autotest(tmpdir):
    dirname = str(tmpdir)
    test = template.DirectoryRender(os.path.join(test_path,'test-autotest'))
    test.render(dirname, {'name':'user'}, {})

    assert are_dir_trees_equal(dirname, os.path.join(test_path,'test-autotest-result'))

def test_autotest_fail(tmpdir):
    dirname = str(tmpdir)
    test = template.DirectoryRender(os.path.join(test_path,'test-autotest2'))

    with pytest.raises(ValueError) as ex:
        test.render(dirname, {'name':'user'}, {})

    assert ex is not None

def test_parse_config(tmpdir):
    conf_file = os.path.join(str(tmpdir), 'config.sq')
    with open(conf_file, 'w') as wfile:
        print('# this is a comment', file=wfile)
        print('conf.d/ atomic:@atomic', file=wfile)
        print('', file=wfile)
        print('httpd.conf user:sean group:@{group.name} mode:0644', file=wfile)

    cfg = {'atomic':True, 'group': {'name': 'dudes'}}
    render = template.DirectoryRender(test_path)
    result = render.parse_config_sq(conf_file, cfg)

    assert len(result) == 2
    assert result[0].filepath == 'conf.d/'
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

    render = template.DirectoryRender(test_path)
    with pytest.raises(ValueError) as ex:
        render.parse_config_sq(conf_file, {})

    assert ex is not None

    conf_file = os.path.join(str(tmpdir), 'config2.sq')
    with open(conf_file, 'w') as wfile:
        print('conf.d/ atomic:true mdoe:0000', file=wfile)

    with pytest.raises(ValueError) as ex:
        render.parse_config_sq(conf_file, {})

    assert ex is not None

    conf_file = os.path.join(str(tmpdir), 'config3.sq')
    with open(conf_file, 'w') as wfile:
        print('conf.d/', file=wfile)

    with pytest.raises(ValueError) as ex:
        render.parse_config_sq(conf_file, {})

    assert ex is not None

def test_get_config():
    config = {'conf.d/' : FileConfig('conf.d/', True, None, None, 0755),
              'conf.d/config' : FileConfig('conf.d/config', False, 'user', 'group', None)}

    already_configured = set()
    assert get_config('conf.d/','conf.d/', config, already_configured) == [config['conf.d/']]
    assert 'conf.d/' in already_configured
    assert get_config('conf.d/','conf.d/', config, already_configured) == []
    assert 'conf.d/' in already_configured

    assert get_config('conf.d/config', 'conf.d/config', config, set()) == [config['conf.d/'], config['conf.d/config']]
    assert get_config('conf.d/non-existant-file', 'conf.d/non-existant-file', config, set()) == [config['conf.d/']]
    assert get_config('non-exist', 'non-exist', config, set()) == []

def test_apply_config(tmpdir):
    tmpdir = str(tmpdir)

    filepath = os.path.join(tmpdir, 'test.txt')
    with open(filepath, 'w') as cfile:
        cfile.write('test')

    apply_config(tmpdir, [FileConfig(filepath, False, None, None, '0777')], False)
    st = os.stat(filepath)
    assert stat.S_IMODE(st.st_mode) == 0777

    filepath = os.path.join(tmpdir, 'test2.txt')
    with open(filepath, 'w') as cfile:
        cfile.write('test2')

    apply_config(tmpdir, [FileConfig(filepath, False, None, None, '0777')], True)
    st = os.stat(filepath)
    # dry run doesn't affect mode
    assert stat.S_IMODE(st.st_mode) == 0777

def test_git_repo(tmpdir):
    dirname = str(tmpdir)
    test = template.DirectoryRender(os.path.join(test_path,'test-git'))
    test.render(dirname, {}, {})

    assert are_dir_trees_equal(dirname, os.path.join(test_path,'test-git-result'))

def test_git_repo_chmod(tmpdir):
    dirname = str(tmpdir)
    test = template.DirectoryRender(os.path.join(test_path,'test-git-chmod'))
    test.render(dirname, {}, {})

    result_dir = os.path.join(test_path,'test-git-result')
    assert are_dir_trees_equal(dirname, result_dir)

    st = os.stat(os.path.join(dirname, 'test', 'install'))
    # Chose some weird mode that wouldn't normally be set
    assert stat.S_IMODE(st.st_mode) == 0604

def test_ext_created_dir(tmpdir):
    dirname = str(tmpdir)
    test = template.DirectoryRender(os.path.join(test_path,'test-ext-created-dir'))
    atomic = test.render(dirname, {}, {})

    assert 'testdir/' in atomic
    assert atomic['testdir/'] == True
    assert 'dir1/testdir/' in atomic
    assert atomic['dir1/testdir/'] == True

    result = os.path.join(dirname, 'testdir')
    assert os.path.isdir(result) == True
    assert len(os.listdir(result)) == 0 # Should be empty

    result = os.path.join(dirname, 'dir1', 'testdir')
    assert os.path.isdir(result) == True
    assert len(os.listdir(result)) == 0 # Should be empty
