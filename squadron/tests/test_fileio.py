from ..fileio.walkhash import walk_hash

def test_basic_walkhash():
    result = walk_hash('fileio_tests/walkhash1')

    assert result == {
            'fileio_tests/walkhash1/file1.txt':'45e3c8923e46f64b4baf68dd127e1871511d74782b1af4109435ebc9b73ad42c',
            'fileio_tests/walkhash1/hello.alpha':'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
            'fileio_tests/walkhash1/dir/a.b':'3028acf5e4c1117ab3d2bfbf5ecffb4d3147c9acb452fb375f27a57acd0bc9b7'
        }
