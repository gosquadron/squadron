import os
from squadron.fileio.symlink import force_create_symlink

def compare_contents(one, two):
    with open(one) as f1:
        with open(two) as f2:
            return f1.read() == f2.read()

def test_symlink(tmpdir):
    tmpdir = str(tmpdir)

    source1 = os.path.join(tmpdir, 'source1')
    with open(source1, 'w') as f:
        f.write('source1\n')

    dest = os.path.join(tmpdir, 'dest')

    force_create_symlink(source1, dest)

    assert os.path.islink(dest)
    assert compare_contents(source1, dest)

    source2 = os.path.join(tmpdir, 'source2')
    with open(source2, 'w') as f:
        f.write('source2\n')

    force_create_symlink(source2, dest)

    assert os.path.islink(dest)
    assert compare_contents(source2, dest)
