import os
from git import Git

def go_to_root(fn):
    """
    Decorator which will execute the decorated function at the root
    of the git hierarchy. It returns to the old directory after
    executing the function
    """

    def wrapped(squadron_dir, *args, **kwargs):
        old_cwd = os.getcwd()
        try:
            if squadron_dir == os.getcwd():
                # We might not be at the root
                root_dir = Git(squadron_dir).rev_parse('--show-toplevel')

                os.chdir(root_dir)
                squadron_dir = root_dir
            return fn(squadron_dir, *args, **kwargs)
        finally:
            os.chdir(old_cwd)
    return wrapped

