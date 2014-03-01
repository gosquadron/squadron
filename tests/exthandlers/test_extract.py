from squadron.exthandlers import extract
from squadron.fileio.dirio import SafeChdir
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
        with SafeChdir(self.directory):
            self.httpd.serve_forever()

def get_config(url, extract_type = None, persist = None):
    ret = {'url': url}

    if extract_type:
        ret['type'] = extract_type

    if persist:
        ret['persist'] = persist

    return ret

@pytest.mark.parametrize("filename",
        ["file.tar.gz",
         "file.tar.bz2",
         "file.tar",
         "file.zip"])
def test_basic(tmpdir, filename):
    tmpdir = str(tmpdir)

    # To serve the files out of the correct directory
    port = get_port()
    http_thread = BackgroundHTTPServer(get_test_path(), port)
    http_thread.start()

    try:
        cfg = json.dumps(get_config('http://localhost:{}/data/{}'.format(port, filename)))
        abs_source = os.path.join(tmpdir, 'input_config')
        with open(abs_source, 'w') as f:
            f.write(cfg)

        dest = os.path.join(tmpdir, 'dest')
        result = extract.ext_extract(abs_source, dest, {}, get_loader())

        assert os.path.exists(os.path.join(dest, 'file.txt')) == True
    finally:
        http_thread.httpd.shutdown()
        http_thread.join()
