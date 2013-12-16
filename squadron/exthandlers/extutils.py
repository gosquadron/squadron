def get_filename(filename):
    """
    Gets the filename from a filename~ext combination. Throws a ValueError
    if there seems to be no filename.

    Keyword arguments:
        filename -- the file to get the base filename from
    """
    try:
        result = filename[:filename.index('~')]
    except ValueError:
        result = filename

    if len(result) == 0:
        raise ValueError('Filename of "{}" is nothing'.format(filename))

    return result
