import os
import pwd
import grp
import errno
from shutil import copyfile
from quik import FileLoader, Template
import urllib
import autotest
from collections import namedtuple
from fileio.dirio import mkdirp
import shutil
from exthandlers import extension_handles
from log import log

def get_sq_ext(filename):
    """
    Gets the squadron extension from filename.
    Keyword arguments:
        filename -- the file to get the extension from
    """
    try:
        return filename[filename.rindex('~')+1:]
    except ValueError:
        return ''

def get_file_ext(filename):
    """
    Gets the extension (or compound extension) from a filename

    Keyword arguments:
        filename -- the file to get the extension from
    """
    root,ext = os.path.splitext(filename)
    if ext.lower() in ['.gz', '.bz2', '.xz']:
        other = os.path.splitext(root)[1]
        if other.lower() in ['.tar']:
            # Make sure we bundle file.tar.gz as 'tar.gz'
            return (other[1:] + ext).lower()

    return ext[1:].lower()


FileConfig = namedtuple('FileConfig', 'filepath atomic user group mode')

def get_config(finalfile, filename, config, already_configured):
    path_items = filename.split(os.path.sep)
    accum = ""
    file_settings = []
    for item in path_items[:-1]:
        # loop over all the directories, but not the filename
        path = os.path.join(accum, item)
        path_and_sep = path + os.path.sep
        if path_and_sep in config and path_and_sep not in already_configured:
            file_settings.append(config[path + os.path.sep])
            already_configured.add(path_and_sep)
        accum = path

    if filename in config and config[filename] not in file_settings:
        if filename not in already_configured:
            file_settings.append(config[filename])
            already_configured.add(filename)

    if os.path.isdir(finalfile):
        new_files = os.listdir(finalfile)
        for f in new_files:
            new_finalfile = os.path.join(finalfile, f)
            new_filename = os.path.join(filename, f)
            file_settings.extend(get_config(new_finalfile, new_filename, config, already_configured))

    return file_settings

def apply_config(base_path, file_configs, dry_run):
    for file_config in file_configs:
        uid = -1
        gid = -1
        if file_config.user is not None:
            uid = pwd.getpwnam(file_config.user).pw_uid
        if file_config.group is not None:
            gid = grp.getgrnam(file_config.group).gr_gid

        actual_file = os.path.join(base_path, file_config.filepath)

        if not dry_run:
            if uid != -1 or gid != -1:
                log.debug("Changing %s to uid %s gid %s", actual_file, uid, gid)
                os.chown(actual_file, uid, gid)
        else:
            if uid != -1 or gid != -1:
                log.info("Would change %s to uid %s gid %s", actual_file, uid, gid)

        if file_config.mode is not None:
            mode = int(file_config.mode, 8)
            log.debug("Changing mode of %s to %s", actual_file, file_config.mode)
            os.chmod(actual_file, mode)


class DirectoryRender:
    def __init__(self, basedir):
        if not os.path.isabs(basedir):
            basedir = os.path.abspath(basedir)
        self.loader = FileLoader(basedir)
        self.basedir = basedir

    def render(self, destdir, inputhash, resources, dry_run = False,
            currpath = "", config = {}):
        """
        Transforms all templates and downloads all files in the directory
        supplied with the input values supplied. Output goes in destdir.

        Keyword arguments:
            destdir -- the directory to put the rendered files into
            inputhash -- the dictionary of input values
        """
        items = sorted(os.listdir(os.path.join(self.basedir, currpath)))

        if currpath == "" and 'config.sq' in items:
            # do config.sq stuff only in the top level directory
            config_items = self.parse_config_sq(
                    os.path.join(self.basedir, 'config.sq'), inputhash)

            real_config = {}
            for config_item in config_items:
                real_config[config_item.filepath] = config_item

            config = real_config
            items.remove('config.sq')

        result = {}
        already_configured = set()
        for filename in items:
            # the path of the source file relative to the basedir
            relpath = os.path.join(currpath, filename)

            # the absolute path of the source file
            abs_source = os.path.join(self.basedir, relpath)

            # the absolute path of the destination file, templated
            dest = self._template(os.path.join(destdir, relpath), inputhash)

            if os.path.isdir(abs_source):
                mkdirp(dest)
                # Needs a slash because this is a directory
                stripped = dest[len(destdir)+1:] + os.path.sep

                key = relpath + os.path.sep
                if key in config:
                    result[key] = config[key].atomic

                apply_config(destdir, get_config(dest, stripped, config, already_configured), dry_run)
                result.update(self.render(destdir, inputhash, resources, dry_run, relpath, config))
            else:
                ext = get_sq_ext(filename)
                if ext in extension_handles:
                    # call the specific handler for this file extension
                    finalfile = extension_handles[ext](**{'loader':self.loader,
                        'inputhash':inputhash,
                        'relpath':relpath,
                        'abs_source': abs_source,
                        'dest':dest,
                        'resources':resources})
                else:
                    # otherwise, just copy the file
                    copyfile(abs_source, dest)
                    finalfile = dest

                finalext = get_file_ext(finalfile)
                stripped = finalfile[len(destdir)+1:]
                if os.path.isdir(finalfile):
                    stripped = stripped + os.path.sep
                    if stripped in config:
                        result[stripped] = config[stripped].atomic

                apply_config(destdir, get_config(finalfile, stripped, config, already_configured), dry_run)

                # if there's an automatic way to test this type of file,
                # try it
                if finalext in autotest.testable:
                    if not autotest.testable[finalext](finalfile):
                        raise ValueError('File {} didn\'t pass validation for {}'.format(finalfile, finalext))

        return result

    def _template(self, item, config):
        template = Template(item)
        return template.render(config)

    def parse_config_sq(self, filename, inputhash):
        """
        Parses a config.sq file which contains metadata about files in this
        directory.

        Keyword arguments:
            filename -- the config.sq file to open
            inputhash -- the service variables to template config.sq with
        """
        # Conversion functions from string to the correct type, str is identity
        convert = {'atomic': bool, 'user':str, 'group':str, 'mode':str}
        require_dir = set(['atomic'])
        result = []

        template = self.loader.load_template(filename)
        contents = template.render(inputhash, loader=self.loader)

        for line in contents.split('\n'):
            # These are the default values
            item = {'atomic': False, 'user':None, 'group':None, 'mode':None}

            if line == "" or line.startswith("#"):
                continue

            args = line.split()
            if len(args) < 2:
                raise ValueError('Line "{}" in file {} isn\'t formatted correctly'.format(line, filename))

            filepath = args[0]
            for arg in args[1:]:
                (key, value) = arg.split(':', 2)

                if key in require_dir:
                    # if this key requires us to be a directory, check
                    if not filepath.endswith(os.path.sep):
                        raise ValueError('Key {} requires entry {} to end with' +
                                ' a slash (must be directory) in file {}'.format(key, filepath, filename))

                #Only do work if we know about this parameter
                if key in convert:
                    item[key] = convert[key](value)
                else:
                    raise ValueError('Unknown config.sq value {} in file {}'.format(key, filename))
            result.append(FileConfig(filepath, item['atomic'], item['user'], item['group'], item['mode']))

        return result

