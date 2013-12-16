from extutils import get_filename

def ext_template(inputhash, relpath, loader, dest, **kwargs):
    """ Renders a ~tpl file"""
    template = loader.load_template(relpath)
    output = template.render(inputhash, loader=loader)

    finalfile = get_filename(dest)
    with open(finalfile, 'w') as outfile:
        outfile.write(output)
        return finalfile
