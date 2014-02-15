import wrap_apt

def schema():
    """
    This returns
    """
    return { 'title': 'apt schema',
            'type': 'string'
            }


def verify(inputhashes):
    """
    """ 
    failed = []
    for package in inputhashes:
        if(wrap_apt.check_package_is_installed(package) == False):
            failed.append(package)
    return failed

def apply(inputhashes, log, **kwargs):
    failed = []
    for package in inputhashes:
        log.error('test')
        if(wrap_apt.install_package(package) == False):
            failed.append(package)
    return failed


