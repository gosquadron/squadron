from ConfigParser import SafeConfigParser, NoSectionError
import socket
import os
from ..log import log

def CONFIG_DEFAULTS():
    return {
        'polltime':'30',
        'keydir':'/etc/squadron/keydir',
        'nodename':socket.getfqdn(),
        'statedir':'/var/squadron',
        'send_status': 'false'
    }

#This is not a func so that we can change it in a test
CONFIG_PATHS = ['/etc/squadron/config',
        '/usr/local/etc/squadron/config',
        os.path.expanduser('~/.squadron/config'),
        ]

def CONFIG_SECTIONS():
    return ['squadron', 'status', 'daemon']

def parse_config(config_file = None, defaults = CONFIG_DEFAULTS()):
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
    parser = SafeConfigParser()
    
    if config_file is None:
        # Try defaults
        parsed_files = parser.read(CONFIG_PATHS)
        log.debug("Using log files: " + str(parsed_files))
    else:
        with open(config_file) as cfile:
            parser.readfp(cfile, config_file)

    if parser.sections():
        log.debug("Original section squadron: " + str(parser.items('squadron')))
        result = defaults.copy()
        for section in CONFIG_SECTIONS():
            try:
                result.update(parser.items(section))
            except NoSectionError:
                pass
        return result
    else:
        raise Exception('No config file could be loaded. Make sure at least one of these exists and can be parsed: ' + str(CONFIG_PATHS))
