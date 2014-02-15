import os
import fnmatch
import json
from log import log

def get_node_info(node_dir, node_name):
    """
    Recurses down the directory trying to find filename wildcards that
    match the given filename. Returns the JSON node info for the closest
    match.

    If there are two wildcards that match, the one that is more
    specific will win.

    Example:
        node_name = 'dev-sea1.api.example.com'

        files = os.listdir(node_dir)
        # Returns ['dev%','dev%.api.example.com', 'staging%']
        get_node_info(node_dir, node_name) = json of 'dev%.api.example.com'

    Keyword arguments:
        node_dir -- the directory to start
        node_name -- the name of the host to match against
    """
    log.debug('entering node.get_node_info')
    result = _descend(node_dir, node_name)

    # sort by length with only the basename and with all hashes removed
    result.sort(lambda x,y: cmp(
        len(os.path.basename(x).translate(None, '%*')), # remove all percents
        len(os.path.basename(y).translate(None, '%*'))))# and asterisks


    ret = {}
    for r in result:
        with open(r) as node_file:
            ret.update(json.loads(node_file.read()))

    log.debug('leaving node.get_node_info: %s', ret)
    return ret

def _descend(base_dir, node_name):
    """
    Recurses down the directory trying to find filename wildcards that
    match the given filename. Returns a list of all wildcards that match.

    Keyword arguments:
        base_dir -- the directory to start
        node_name -- the name of the host to match against
    """
    files = os.listdir(base_dir)
    result = []
    for f in files:
        srcfile = os.path.join(base_dir, f)
        if os.path.isdir(srcfile):
            result.extend(_descend(srcfile, node_name))
        else:
            if fnmatch.filter([node_name], f.replace('%','*')):
                result.append(srcfile)
    return result



