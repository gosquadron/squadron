import wrap_apt
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
            log.debug("Apt package %s is not installed", package)
        else:
            log.debug("Apt package %s was installed already", package)
    return failed

def apply(inputhashes, log, **kwargs):
    failed = []
    for package in inputhashes:
        if(wrap_apt.install_package(package) == False):
            failed.append(package)
            log.debug("Failed to install apt package: %s", package)
        else:
            log.debug("Installed successfully apt package: %s", package)
    return failed


