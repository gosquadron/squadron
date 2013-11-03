from .. import initialize
import os

def test_basic(tmpdir):
    tmpdir = str(tmpdir)
    print "basic: " + tmpdir
    initialize.init(tmpdir)

    items = os.listdir(tmpdir)
    assert len(items) > 0

def test_service(tmpdir):
    tmpdir = str(tmpdir)
    print "service: " + tmpdir
    initialize.initService(tmpdir, 'api')

    items = os.listdir(os.path.join(tmpdir, 'api'))

    assert len(items) > 0
