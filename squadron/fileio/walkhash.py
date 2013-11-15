from hashlib import sha256
import os

def walk_hash(directory):
    """
    Walks the directory and generates a SHA-256 hash for each
    file in the directory. Returns a dictionary of filename
    to SHA-256 hash

    Keyword arguments:
        directory -- the directory to generate the hashes for

    """
    ret = {}
    for root, dirs, files in os.walk(directory):
        for filename in files:
            path_name = os.path.join(root, filename)
            with open(path_name) as tohash:
                ret[path_name] = sha256(tohash.read()).hexdigest()
    return ret
