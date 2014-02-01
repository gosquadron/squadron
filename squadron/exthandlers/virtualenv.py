import tempfile
import os
import subprocess
from extutils import get_filename

def ext_virtualenv(abs_source, dest, **kwargs):
    requirements=[]

    # Create virtualenv
    virtual_env = get_filename(dest)
    subprocess.check_call(['virtualenv', virtual_env])

    # Set up environment
    pip_env = os.environ.copy()
    pip_env['VIRTUAL_ENV'] = virtual_env
    pip_env['PATH'] = '{}/bin:{}'.format(virtual_env, pip_env['PATH'])

    if 'PYTHONHOME' in pip_env:
        del pip_env['PYTHONHOME']

    # Install requirements
    pip_bin = os.path.join(virtual_env, 'bin', 'pip')
    pip = subprocess.Popen([pip_bin, 'install', '-r', abs_source],
            env=pip_env)
    ret_code = pip.wait()

    if ret_code != 0:
        raise subprocess.CalledProcessError(ret_code, pip_bin)

    return virtual_env
