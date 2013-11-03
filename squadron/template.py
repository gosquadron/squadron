import os
import errno
from shutil import copyfile
from quik import Template, FileLoader
import urllib
import autotest

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

class DirectoryRender:
    def __init__(self, basedir):
        self.loader = FileLoader(basedir)
        self.basedir = basedir

    def render(self, destdir, inputhash, currpath = ""):
        """
        Transforms all templates and downloads all files in the directory
        supplied with the input values supplied. Output goes in destdir.

        Keyword arguments:
            destdir -- the directory to put the rendered files into
            inputhash -- the dictionary of input values
        """
        items = os.listdir(os.path.join(self.basedir, currpath))

        for filename in items:
            # the path of the source file relative to the basedir
            relpath = os.path.join(currpath, filename)

            # the absolute path of the source file
            abs_source = os.path.join(self.basedir, relpath)

            # the absolute path of the destination file
            dest = os.path.join(destdir, relpath)
            if os.path.isdir(abs_source):
                mkdirp(dest)
                self.render(destdir, inputhash, relpath)
            else:
                ext = get_ext(filename)
                if ext in extension_handles:
                    # call the specific handler for this file extension
                    finalfile = extension_handles[ext](self.loader, inputhash, relpath, abs_source, dest)
                    finalext = get_ext(finalfile)

                    # if there's an automatic way to test this type of file,
                    # try it
                    if finalext in autotest.testable:
                        if not autotest.testable[finalext](finalfile):
                            raise ValueError('File {} didn\'t pass validation for {}'.format(finalfile, finalext))
                else:
                    # otherwise, just copy the file
                    copyfile(abs_source, dest)


