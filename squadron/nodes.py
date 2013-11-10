import os
import fnmatch
import json

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
        # Returns ['dev*','dev*.api.example.com', 'staging*']
        get_node_info(node_dir, node_name) = json of 'dev*.api.example.com'

    Keyword arguments:
        node_dir -- the directory to start
        node_name -- the name of the host to match against
    """
    result = _descend(node_dir, node_name)

    len_closest = -1
    closest = None
    for r in result:
        base_str = os.path.basename(r).translate(None, '*') # remove all asterisks
        if len(base_str) > len_closest:
            closest = r
            len_closest = len(base_str)

    if closest == None:
        # No match
        return None
    else:
        with open(closest) as node_file:
            return json.loads(node_file.read())

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
            if fnmatch.filter([node_name], f):
                result.append(srcfile)
    return result



