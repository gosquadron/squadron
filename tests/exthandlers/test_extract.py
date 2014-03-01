from squadron.exthandlers import extract
from squadron.fileio.dirio import SafeChdir
import SocketServer
import SimpleHTTPServer
import threading
from quik import FileLoader
import os
import json

PORT = 8903

def get_test_path():
    return os.path.dirname(os.path.realpath(__file__))

def get_loader():
    return FileLoader(os.getcwd())

class BackgroundHTTPServer(threading.Thread):
    def __init__(self, directory):
        threading.Thread.__init__(self)
        self.directory = directory
        self.httpd = SocketServer.ForkingTCPServer(('127.0.0.1', PORT),
            SimpleHTTPServer.SimpleHTTPRequestHandler)

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

def test_basic(tmpdir):
    tmpdir = str(tmpdir)

    # To serve the files out of the correct directory
    http_thread = BackgroundHTTPServer(get_test_path())
    http_thread.start()

    try:
        cfg = json.dumps(get_config('http://localhost:{}/data/file.tar.gz'.format(PORT)))
        abs_source = os.path.join(tmpdir, 'input_config')
        with open(abs_source, 'w') as f:
            f.write(cfg)

        dest = os.path.join(tmpdir, 'dest')
        result = extract.ext_extract(abs_source, dest, {}, get_loader())

        assert os.path.exists(os.path.join(dest, 'file.txt')) == True
    finally:
        http_thread.httpd.shutdown()
        http_thread.join()
