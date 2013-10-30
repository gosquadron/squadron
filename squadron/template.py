import os
import errno
from shutil import copyfile
from quik import Template, FileLoader
import urllib

def mkdirp(dirname):
    try:
        os.mkdir(dirname)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(dirname):
            print "dir already exists {}".format(dirname)
            pass

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
            relpath = os.path.join(currpath, filename)
            cur = os.path.join(self.basedir, relpath)
            dest = os.path.join(destdir, relpath)
            if os.path.isdir(cur):
                print "Making directory {}".format(dest)
                mkdirp(dest)
                self.render(destdir, inputhash, relpath)
            else:
                print "cur {} is not a directory".format(cur)
                if filename.endswith('.tpl'):
                    template = self.loader.load_template(relpath)
                    output = template.render(inputhash, loader=self.loader)
                    with open(dest.rstrip('.tpl'), 'w') as outfile:
                        outfile.write(output)
                elif filename.endswith('.download'):
                    with open(cur, 'r') as downloadfile:
                        (url, checksum) = downloadfile.read().split(None, 3)

                        print "Downloading {} to {}".format(url, dest)
                        urllib.urlretrieve(url, dest.rstrip('.download'))
                else:
                    copyfile(cur, dest)

