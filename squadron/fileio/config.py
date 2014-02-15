from ConfigParser import SafeConfigParser, NoSectionError
import sys
import socket
import os
from ..log import log
from ..exceptions import UserException
import logging
import logging.handlers

#For some reason we're reading the config file twice.
#Once that is fixed this should be removed
PARSED_LOG_CONFIG = False

def CONFIG_DEFAULTS():
    return {
        'polltime':'30',
        'keydir':'/etc/squadron/keydir',
        'nodename':socket.getfqdn(),
        'statedir':'/var/squadron',
        'send_status': 'false',
    }

#This is not a func so that we can change it in a test
CONFIG_PATHS = ['/etc/squadron/config',
        '/usr/local/etc/squadron/config',
        os.path.expanduser('~/.squadron/config'),
        ]

def CONFIG_SECTIONS():
    return ['squadron', 'status', 'daemon', 'log']

def VALID_LOG_HANDLERS():
    return ['file', 'stream', 'rotatingfile']

def VALID_STREAMS():
    return ['stdout', 'stderr']

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
    global PARSED_LOG_CONFIG
    
    if config_file is None:
        # Try defaults
        parsed_files = parser.read(CONFIG_PATHS)
        log.debug("Using config files: %s", parsed_files)
    else:
        log.debug("Using config file: %s", config_file)
        with open(config_file) as cfile:
            parser.readfp(cfile, config_file)

    #Here we setup any extra logging
    if 'log' in parser.sections() and not PARSED_LOG_CONFIG:
        PARSED_LOG_CONFIG = True
        for item in parser.items('log'):
            try:
                #key is just a friendly name and it's not used
                #reason is that key's are usually unique in these configs
                logline = item[1].split(' ')
                if(len(logline) < 2):
                    log.error('Invalid log config passed: %s', item)
                    continue

                #parse level
                levelStr = logline[0]
                level = getattr(logging, levelStr.upper(), None)
                if not isinstance(level, int):
                    log.error('Invalid log level passed for: %s', item)
                    continue
    
                #parse handler
                handler = logline[1].lower()
                if not handler in VALID_LOG_HANDLERS():
                    log.error('Invalid log handler passed for: %s', item)
                    continue
    
                if(handler == 'file'):
                    if(len(logline) < 3):
                        log.error('File log handler needs output file as last parameter: %s', item)
                        continue
                    param = logline[2]
                    fh = logging.FileHandler(param, 'a', None, False)
                    fh.setLevel(level)
                    log.addHandler(fh)
    
                if(handler == 'stream'):
                    if(len(logline) < 3):
                        log.error('File log handler needs stream such as sys.stderr as last parameter: %s', item)
                        continue
                    param = logline[2].lower()
                    if not param in VALID_STREAMS():
                        log.error('Invalid stream param passed: %s', item)
                        continue

                    #TODO: Do this better (casting)
                    if param == 'stdout':
                        param = sys.stdout
                    if param == 'stderr':
                        param = sys.stderr

                    sh = logging.StreamHandler(param)
                    sh.setLevel(level)
                    log.addHandler(sh)
                if(handler == 'rotatingfile'):
                    if(len(logline) < 4):
                        log.error('Rotating log handler needs a file name, max size and maxCount')
                        continue
                    #TODO: Verify parameters
                    rh = logging.handlers.RotatingFileHandler(logline[2], 'a', logline[3], logline[4])
                    rh.setLevel(level)
                    log.addHandler(rh)
            except:
                log.error('Error creating log handler for %s', item)
                raise

    if parser.sections():
        log.debug("Original section squadron: %s", parser.items('squadron'))
        result = defaults.copy()
        for section in CONFIG_SECTIONS():
            try:
                result.update(parser.items(section))
            except NoSectionError:
                pass
        return result
    else:
        raise UserException('No config file could be loaded. Make sure at least one of these exists and can be parsed: ' + str(CONFIG_PATHS))

    
