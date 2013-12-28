import os
import errno
import tempfile

def force_create_symlink(src, dst):
    try:
        os.symlink(src, dst)
    except OSError as e:
        if e.errno == errno.EEXIST:
            (handle, tmpfile) = tempfile.mkstemp()
            os.close(handle)
            os.remove(tmpfile)
            try:
                os.symlink(src, tmpfile)
                os.rename(tmpfile, dst)
            except:
                os.remove(tmpfile)
                raise
        else:
            raise e
