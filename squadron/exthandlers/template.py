from extutils import get_filename

def render(relpath, inputhash, loader):
    template = loader.load_template(relpath)
    return template.render(inputhash, loader=loader)

def ext_template(inputhash, relpath, loader, dest, **kwargs):
    """ Renders a ~tpl file"""
    output = render(relpath, inputhash, loader)

    finalfile = get_filename(dest)
    with open(finalfile, 'w') as outfile:
        outfile.write(output)
        return finalfile
