from .dir import ext_dir
from .extract import ext_extract
from .makegit import ext_git
from .download import ext_download
from .template import ext_template
from .virtualenv import ext_virtualenv

extension_handles = {
    'dir':ext_dir,
    'git':ext_git,
    'download':ext_download,
    'virtualenv':ext_virtualenv,
    'tpl':ext_template,
    'extract':ext_extract
}
