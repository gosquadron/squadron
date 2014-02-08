from log import log
import os

def _make_loader(filename):
    def inner():
        with open(filename) as f:
            return f.read()
    return inner

def load_resources(squadron_dir):
    """
    Returns a dictionary of function to all of the resources in the resources
    directory so that they can be loaded on demand.

    Keyword arguments:
        squadron_dir -- the squadron directory
    """
    resource_dir = os.path.join(squadron_dir, 'resources')
    ret = {}

    for root, dirs, files in os.walk(resource_dir):
        base = root[len(resource_dir)+1:]
        for filename in files:
            rel_path = os.path.join(base, filename)
            log.debug('Loading resource %s', rel_path)
            ret[rel_path] = _make_loader(os.path.join(resource_dir, rel_path))
    log.info("Loaded %s resources", len(ret))
    return ret
