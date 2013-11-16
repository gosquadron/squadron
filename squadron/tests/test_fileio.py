from ..fileio.walkhash import walk_hash, hash_diff

def test_basic_walkhash():
    result = walk_hash('fileio_tests/walkhash1')

    assert result == {
            'fileio_tests/walkhash1/file1.txt':'45e3c8923e46f64b4baf68dd127e1871511d74782b1af4109435ebc9b73ad42c',
            'fileio_tests/walkhash1/hello.alpha':'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
            'fileio_tests/walkhash1/dir/a.b':'3028acf5e4c1117ab3d2bfbf5ecffb4d3147c9acb452fb375f27a57acd0bc9b7'
        }

def test_basic_hash_diff():
    old = {
        'dir1/a.txt':'abcdef',
        'dir2/b.txt':'012345',
        'dir2/c.txt':'01x345',
    }

    new_hash = {
        'dir1/a.txt':'abcdef',
        'dir2/b.txt':'012346', # different
        'other.txt':'always'
    }

    paths_changed = ['dir2/b.txt']
    new_paths = ['other.txt']

    assert (paths_changed, new_paths) == hash_diff(old, new_hash)
