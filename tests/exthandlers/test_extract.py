from squadron.exthandlers import extract
from squadron.fileio.dirio import SafeChdir, makedirsp
import SocketServer
import SimpleHTTPServer
import threading
from quik import FileLoader
import os
import json
import pytest
import random

def get_port():
    return 8904

def get_test_path():
    return os.path.dirname(os.path.realpath(__file__))

def get_loader():
    return FileLoader(os.getcwd())

class ReuseTCPServer(SocketServer.TCPServer):
    allow_reuse_address = True

class BackgroundHTTPServer(threading.Thread):
    def __init__(self, directory, port):
        threading.Thread.__init__(self)
        self.directory = directory
        self.httpd = ReuseTCPServer(('127.0.0.1', port), SimpleHTTPServer.SimpleHTTPRequestHandler)

    def run(self):
        # To serve the files out of the correct directory
        with SafeChdir(self.directory):
            self.httpd.serve_forever()

def get_config(url, extract_type = None, persist = None, copy = None):
    ret = {'url': url}

    if extract_type is not None:
        ret['type'] = extract_type

    if persist is not None:
        ret['persist'] = persist

    if copy is not None:
        ret['copy'] = copy

    return ret

@pytest.mark.parametrize("filename,filetype",
        [("file.tar.gz",None),
         ("file.tar.bz2",None),
         ("file.tar",None),
         ("file.tar","tar"),
         ("file.zip",None),
         ("file.zip","zip")])
def test_basic(tmpdir, filename, filetype):
    tmpdir = str(tmpdir)

    port = get_port()
    http_thread = BackgroundHTTPServer(get_test_path(), port)
    http_thread.start()

    try:
        cfg = json.dumps(get_config('http://localhost:{}/data/{}'.format(port, filename), filetype))
        abs_source = os.path.join(tmpdir, 'input_config')
        with open(abs_source, 'w') as f:
            f.write(cfg)

        dest = os.path.join(tmpdir, 'dest')
        result = extract.ext_extract(abs_source, dest, {}, get_loader())

        assert os.path.exists(os.path.join(dest, 'file.txt')) == True
    finally:
        http_thread.httpd.shutdown()
        http_thread.join()

@pytest.mark.parametrize("filename,persist",
        [("file.tar.gz",True),
         ("file.tar.bz2",False),
         ("file.tar",True),
         ("file.zip",False)])
def test_copy(tmpdir, filename, persist):
    tmpdir = str(tmpdir)

    port = get_port()
    http_thread = BackgroundHTTPServer(get_test_path(), port)
    http_thread.start()

    try:
        if persist:
            directory = 'dir1'
        else:
            directory = os.path.join(tmpdir, 'dir1')

        copy = [{'from':'*.txt',
                 'to': directory + os.path.sep}]

        cfg = json.dumps(get_config('http://localhost:{}/data/{}'.format(port, filename),
            persist=persist, copy=copy))

        print "Cfg: {}".format(cfg)

        abs_source = os.path.join(tmpdir, 'input_config')
        with open(abs_source, 'w') as f:
            f.write(cfg)

        dest = os.path.join(tmpdir, 'dest')
        if persist:
            dest_subdir = os.path.join(dest, directory)
        else:
            dest_subdir = directory
        makedirsp(dest_subdir)

        result = extract.ext_extract(abs_source, dest, {}, get_loader())

        assert os.path.exists(os.path.join(dest_subdir, 'file.txt')) == True
        if persist:
            assert os.path.exists(dest) == True
            assert result is not None
        else:
            assert os.path.exists(dest) == False
            assert result is None
    finally:
        http_thread.httpd.shutdown()
        http_thread.join()
