import urllib
from extutils import get_filename

def ext_download(loader, inputhash, abs_source, dest, **kwargs):
    """ Downloads a ~download file"""
    template = loader.load_template(abs_source)
    output = template.render(inputhash, loader=loader)

    # split on whitespace
    (url, checksum) = output.split(None, 3)

    finalfile = get_filename(dest)
    urllib.urlretrieve(url, finalfile)

    return finalfile
