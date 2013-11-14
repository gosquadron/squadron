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

