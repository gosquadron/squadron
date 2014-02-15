import wrap_apt
#from log import log
def schema():
    """
    This returns
    """
    return { 'title': 'apt schema',
            'type': 'string'
            }


def verify(inputhashes, log, **kwargs):
    """
    """ 
    failed = []
    for package in inputhashes:
        if(wrap_apt.check_package_is_installed(package) == False):
            failed.append(package)
            log.debug("Apt package " + str(package) + " is not installed")
        else:
            log.debug("Apt package " + str(package) + " was installed already")
    return failed

def apply(inputhashes, log, **kwargs):
    failed = []
    for package in inputhashes:
        if(wrap_apt.install_package(package) == False):
            failed.append(package)
            log.debug("Failed to install apt package: " + str(package))
        else:
            log.debug("Installed successfully apt package: " + str(package))
    return failed


