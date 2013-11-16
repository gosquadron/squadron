import os
import errno

def mkdirp(dirname):
    return _ignore_exist(dirname, os.mkdir)

def makedirsp(dirname):
    return _ignore_exist(dirname, os.makedirs)

def _ignore_exist(dirname, func):
    try:
        func(dirname)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(dirname):
            pass


class SafeChdir:
    def __init__(self, new_path):
        self.saved_path = os.getcwd()
        self.new_path = new_path

    def __enter__(self):
        os.chdir(self.new_path)

    def __exit__(self, type, value, traceback):
        os.chdir(self.saved_path)
