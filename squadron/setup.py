from log import log
import readline
import os
from fileio.dirio import makedirsp
from initialize import create_json

config = """
[daemon]
polltime = 30

[squadron]
keydir = {}
nodename = override.example.com
statedir = {}
send_status = false

[status]
status_host = status.gosquadron.com
status_apikey = ABCDEF12345
status_secret = 8d4ce3db954ab1bed870ce682e6765ec24a1227352b3d2688170ecaefda1165c 
"""

def setup(etcdir, vardir):
    """ Prompts the user if necessary to set up directories """
    is_root = os.geteuid() == 0
    default_etc = {
            True: '/etc/squadron',
            False: os.path.join(os.path.expanduser('~'),'.squadron')
        }
    default_var = {
            True: '/var/squadron',
            False: os.path.join(os.path.expanduser('~'),'.squadron', 'state')
        }

    if not etcdir:
        result = raw_input("Location for config [{}]: ".format(default_etc[is_root]))
        etcdir = result if result else default_etc[is_root]

    if not vardir:
        result = raw_input("Location for state [{}]: ".format(default_var[is_root]))
        vardir = result if result else default_var[is_root]

    return init_system(etcdir, vardir)


def init_system(etcdir, vardir):
    """ Initializes the system with system wide config files """

    if etcdir:
        log.info("Initializing config dir %s", etcdir)
        makedirsp(etcdir)
        with open(os.path.join(etcdir, 'config'), 'w') as cfile:
            cfile.write(config.format(os.path.join(etcdir, 'keys'), vardir))

    if vardir:
        log.info("Initializing state dir %s", vardir)
        makedirsp(vardir)
        create_json(os.path.join(vardir, 'info.json'))

    return True
