import os
import jsonschema
import imp
import importlib
import sys

class StateHandler:
    def __init__(self, library_dir):
        self.library_dir = library_dir

    def apply(self, library_name, inputhash, dry_run = False):
        """
        Changes the state of the system according to what the module
        specified does

        Keyword arguments:
            library_name -- the python module to load
            inputhash -- the list of dictionaries of config for the library
            dry_run -- whether or not to actually change the system
        """
        if library_name not in sys.modules:
            try:
                imp.acquire_lock()
                mod = imp.find_module(library_name, [self.library_dir])
                imp.load_module(library_name, *mod)
            except ImportError:
                print "Couldn't find module in dir {}".format(self.library_dir)
                raise
            finally:
                if imp.lock_held():
                    imp.release_lock()

        library = importlib.import_module(library_name)
        schema = library.schema()

        for item in inputhash:
            jsonschema.validate(item, schema)

        failed = library.verify(inputhash)

        if not dry_run:
            library.apply(failed)
            failed = library.verify(inputhash)
            if len(failed) > 0:
                print "Failed for good on {}".format(failed)

        return failed
