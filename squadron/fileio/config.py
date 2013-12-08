from ConfigParser import SafeConfigParser
import socket
import os

def config_defaults():
    return {
        'polltime':'30m',
        'keydir':'/etc/squadron/keydir',
        'status':'status.gosquadron.com',
        'nodename':socket.getfqdn(),
        'statedir':'/var/squadron'
    }

def parse_config(defaults, config_file = None):
    """
    Parses a given config file using SafeConfigParser. If the specified
    config_file is None, it searches in the usual places. Returns a
    dictionary of config keys to their values.

    Keyword arguments:
        defaults -- the default global values for the config
        config_file -- the configuration file to read config from. If
            None, searches for system-wide configuration and from
            the local user's configuration.
    """
    parser = SafeConfigParser(defaults)

    if config_file is None:
        # Try defaults
        parser.read(['/etc/squadron/config',os.path.expanduser('~/.squadron/config')])
    else:
        with open(config_file) as cfile:
            parser.readfp(cfile, config_file)

    if parser.sections():
        return dict(parser.items('squadron'))
    else:
        return {}
