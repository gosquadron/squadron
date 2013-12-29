import tempfile
import os
import subprocess
from extutils import get_filename
from stat import *

def _make_exec(path):
    st = os.stat(path)
    os.chmod(path, st.st_mode | S_IXUSR | S_IXGRP | S_IXOTH)

def ext_virtualenv(abs_source, dest, **kwargs):
    requirements=[]
    with open(abs_source) as vfile:
        for line in vfile.readlines():
            if line.startswith('#'):
                # Metadata or comment
                1
            else:
                requirements.append(line.strip())

    # Create virtualenv
    virtual_env = get_filename(dest)
    subprocess.check_call(['virtualenv', virtual_env])

    # Mark everything but activate* in bin/ executable
    bin_dir = os.path.join(virtual_env, 'bin')
    for f in os.listdir(bin_dir):
        if not f.startswith('activate'):
            _make_exec(os.path.join(bin_dir, f))

    if requirements:
        # Write out requirements file
        fd, req_file = tempfile.mkstemp('.sq','requirements')

        with os.fdopen(fd, 'w') as f:
            for line in requirements:
                f.write(line + '\n')

        try:
            # Set up environment
            pip_env = os.environ.copy()
            pip_env['VIRTUAL_ENV'] = virtual_env
            pip_env['PATH'] = '{}/bin:{}'.format(virtual_env, pip_env['PATH'])

            if 'PYTHONHOME' in pip_env:
                del pip_env['PYTHONHOME']

            # Install requirements
            pip_bin = os.path.join(virtual_env, 'bin', 'pip')
            pip = subprocess.Popen([pip_bin, 'install', '-r', req_file],
                    env=pip_env)
            ret_code = pip.wait()

            if ret_code != 0:
                raise subprocess.CalledProcessError(ret_code, pip_bin)
        finally:
            os.remove(req_file)

    return virtual_env
