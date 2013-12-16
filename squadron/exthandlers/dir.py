from extutils import get_filename
import os

def ext_dir(dest, **kwargs):
    finalfile = get_filename(dest)
    os.mkdir(finalfile)
    return finalfile
