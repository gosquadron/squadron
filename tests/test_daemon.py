import mock
from squadron import daemon
from helper import get_test_path
import os
import threading
import pytest
from squadron import log

log.setup_log('DEBUG', console=True)

test_path = os.path.join(get_test_path(), 'daemon_tests')

@pytest.mark.parametrize("webhooks,config_file",[
    (False,"simple"),
    (True,"webhooks"),
])
def test_basic(tmpdir, webhooks, config_file):
    tmpdir = str(tmpdir)

    config_file = os.path.join(test_path, config_file)
    with mock.patch('squadron.main.get_squadron_dir') as dirmock:
        dirmock.return_value = tmpdir
 
        # It's a little odd where this needs to be patched, see:
        # http://www.voidspace.org.uk/python/mock/patch.html#id1
        with mock.patch('squadron.daemon.Repo') as gitmock:
            # The raw git interface object
            git = mock.MagicMock()
            git.checkout.return_value = 0
            git.pull.return_value = 0

            # The git repository object
            repo = mock.MagicMock()
            repo.git.return_value = git

            gitmock.return_value = repo
            with mock.patch('squadron.notify.server.get_server') as getservermock:
                # This is only used for webhooks
                threadmock = mock.MagicMock()
                servermock = mock.MagicMock()
                getservermock.return_value = (threadmock, servermock)

                with mock.patch('squadron.main.go') as mainmock:
                    node_name = 'test'

                    # We want to exit the loop the first time, so give it two
                    # seconds to finish
                    exit_loop = threading.Event()
                    timer = threading.Timer(2, lambda: exit_loop.set())
                    timer.start()

                    # The wait here ensures the timer will have expired
                    daemon.daemonize(tmpdir, config_file, 3, 'blank',
                            node_name, exit_loop)

                    mainmock.assert_called_with(tmpdir, node_name=node_name,
                            config_file=config_file, dry_run=False, dont_rollback=True)

                if webhooks:
                    assert getservermock.called
                    assert servermock.stop.called
                    assert threadmock.join.called

            assert git.checkout.called_with('master')
            assert git.pull.called_with('--rebase')

        assert dirmock.called


