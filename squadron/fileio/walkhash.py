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
            if filename != '.lock':
                # Skip .lock files, as they're unimportant
                with open(path_name) as tohash:
                    ret[path_name] = sha256(tohash.read()).hexdigest()
    return ret

def hash_diff(old_hash, new_hash):
    """
    Returns the keys in new_hash that have different values
    in old_hash. Also returns keys that are in new_hash but not
    in old_hash.

    Keyword arguments:
        old_hash -- the dictionary of hashes for the old directory
        new_hash -- the dictionary of hashes for the new directory
    """
    paths_changed = []
    new_paths = []

    for key, value in new_hash.items():
        if key in old_hash:
            if value != old_hash[key]:
                paths_changed.append(key)
        else:
            new_paths.append(key)

    return (paths_changed, new_paths)
