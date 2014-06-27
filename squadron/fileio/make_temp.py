import os
from .lock import FileLock
from .dirio import mkdirp
from shutil import rmtree

def make_temp(temp_dir, prefix, keep_this_file=None, keep_num=5):
    def parse_num(path):
        """
        parse the number out of a path (if it matches the prefix)

        Borrowed from py.path
        """
        if path.startswith(prefix):
            try:
                return int(path[len(prefix):])
            except ValueError:
                pass

    lockfile = os.path.join(temp_dir, prefix + 'lock')
    with FileLock(temp_dir, lockfile):
        files = os.listdir(temp_dir)

        oldest = None
        youngest = None
        for f in files:
            num = parse_num(f)
            if num:
                if oldest is None or oldest > num:
                    oldest = num
                if youngest is None or youngest < num:
                    youngest = num


        if youngest is None or oldest is None:
            index = '1'
        elif youngest - oldest < keep_num:
            index = str(youngest + 1)
        else:
            index = str(youngest + 1)
            # Remove files
            for i in range(oldest, youngest - keep_num):
                to_delete = os.path.join(temp_dir, prefix + str(i))
                if to_delete != keep_this_file:
                    rmtree(os.path.join(temp_dir, prefix + str(i)), True)

        temp = os.path.join(temp_dir, prefix + index)
        mkdirp(temp)
        return temp



