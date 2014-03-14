import subprocess
import re

def schema():
    """
    This returns the schema for this state library
    """
    return { '$schema': 'http://json-schema.org/draft-04/schema#',
             'description': 'Describes one npm pacakge to install globally',
             'type':'string',
           }

grab_version = re.compile('([\w\d_-]+)@(.+)$')

def get_installed():
    p = subprocess.Popen('npm list --global'.split(),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, _ = p.communicate()
    p.wait()

    result = {}
    for line in out.split('\n'):
        match = grab_version.search(line)
        if match:
            result[match.group(1)] = match.group(2)

    return result

def verify(inputhashes, log, **kwargs):
    """
    Checks if the npm packages are installed
    """
    failed = []

    installed = get_installed()

    for package in inputhashes:
        pkg = package.split('@')[0]

        # TODO: check version
        if pkg not in installed:
            failed.append(package)
            log.debug('npm package %s needs to be installed', package)
    return failed

def install_package(package):
    return 0 == subprocess.call(['npm', 'install', package, '--global'])

def apply(inputhashes, log, **kwargs):
    """
    Installs npm packages globally
    """
    failed = []
    for package in inputhashes:
        if not install_package(package):
            log.error('Couldn\'t install npm package %s', package)
            failed.append(package)
    return failed


