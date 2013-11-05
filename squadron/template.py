import os
import pwd
import grp
import errno
from shutil import copyfile
from quik import Template, FileLoader
import urllib
import autotest
from collections import namedtuple

def mkdirp(dirname):
    try:
        os.mkdir(dirname)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(dirname):
            pass

def ext_template(loader, inputhash, relpath, cur, dest):
    """ Renders a .tpl file"""
    template = loader.load_template(relpath)
    output = template.render(inputhash, loader=loader)

    finalfile = dest.rstrip('.tpl')
    with open(finalfile, 'w') as outfile:
        outfile.write(output)
        return finalfile

def ext_download(loader, inputhash, relpath, cur, dest):
    """ Downloads a .download file"""
    with open(cur, 'r') as downloadfile:
        # split on whitespace
        (url, checksum) = downloadfile.read().split(None, 3)

        finalfile = dest.rstrip('.download')
        urllib.urlretrieve(url, finalfile)
        return finalfile

extension_handles = {'tpl' : ext_template, 'download' : ext_download}

def get_ext(filename):
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
def parse_config(filename):
    """
    Parses a config.sq file which contains metadata about files in this
    directory.

    Keyword arguments:
        filename -- the config.sq file to open
    """
    # Conversion functions from string to the correct type, str is identity
    convert = {'atomic': bool, 'user':str, 'group':str, 'mode':str}
    result = []
    with open(filename) as cfile:
        for line in cfile:
            # These are the default values
            item = {'atomic': False, 'user':None, 'group':None, 'mode':None}

            args = line.split()
            if len(args) < 2:
                raise ValueError('Line "{}" in file {} isn\'t formatted correctly'.format(line, filename))

            filepath = args[0]
            for arg in args[1:]:
                (key, value) = arg.split(':', 2)
                #Only do work if we know about this parameter
                if key in convert:
                    item[key] = convert[key](value)
                else:
                    raise ValueError('Unknown config.sq value {} in file {}'.format(key, filename))
            result.append(FileConfig(filepath, item['atomic'], item['user'], item['group'], item['mode']))
    return result

def get_config(filename, config):
    path_items = filename.split('/')
    accum = ""
    file_setting = FileConfig(filename, False, None, None, None)
    for item in path_items[:-1]:
        # loop over all the directories, but not the filename
        path = os.path.join(accum, item)
        if path + '/' in config:
            file_setting = config[path + '/']

    if filename in config:
        file_setting = config[filename]

    return file_setting

def apply_config(filepath, file_config):
    uid = -1
    gid = -1
    if file_config.user is not None:
        uid = pwd.getpwnam(file_config.user).pw_uid
    if file_config.group is not None:
        gid = grp.getgrnam(file_config.group).gr_gid

    os.chown(filepath, uid, gid)

    if file_config.mode is not None:
        os.chmod(filepath, int(file_config.mode, 8))


class DirectoryRender:
    def __init__(self, basedir):
        self.loader = FileLoader(basedir)
        self.basedir = basedir

    def render(self, destdir, inputhash, currpath = "", config = {}):
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
            config_items = parse_config(os.path.join(self.basedir, 'config.sq'))
            real_config = {}
            for config_item in config_items:
                real_config[config_item.filepath] = config_item

            config = real_config
            items.remove('config.sq')

        for filename in items:
            # the path of the source file relative to the basedir
            relpath = os.path.join(currpath, filename)

            # the absolute path of the source file
            abs_source = os.path.join(self.basedir, relpath)

            # the absolute path of the destination file
            dest = os.path.join(destdir, relpath)
            if os.path.isdir(abs_source):
                mkdirp(dest)
                self.render(destdir, inputhash, relpath, config)
            else:
                ext = get_ext(filename)
                if ext in extension_handles:
                    # call the specific handler for this file extension
                    finalfile = extension_handles[ext](self.loader, inputhash, relpath, abs_source, dest)
                else:
                    # otherwise, just copy the file
                    copyfile(abs_source, dest)
                    finalfile = dest

                finalext = get_ext(finalfile)
                stripped = finalfile[len(destdir)+1:]
                apply_config(finalfile, get_config(stripped, config))

                # if there's an automatic way to test this type of file,
                # try it
                if finalext in autotest.testable:
                    if not autotest.testable[finalext](finalfile):
                        raise ValueError('File {} didn\'t pass validation for {}'.format(finalfile, finalext))

