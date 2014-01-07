Installation
============

Get it from PyPI::

    > pip install sphinx-better-theme

Or `download the zip file`_ and run the usual command::

    > python setup.py install

.. _download the zip file: https://github.com/irskep/sphinx-better-theme/archive/master.zip

Once the package is installed, make these changes to :file:`conf.py` to direct
Sphinx to use the theme::

    from better import better_theme_path
    html_theme_path = [better_theme_path]
    html_theme = 'better'

Read the Docs Configuration
---------------------------

Using sphinx-better-theme with `Read the Docs`_ is easy. You just need to tell
it to install the package.

.. _Read the Docs: https://readthedocs.org/

First, create a :file:`requirements.txt` file just for your docs. It should
look like this::

    sphinx-better-theme==0.1.4
    # other dependencies for your docs if any

I suggest putting it in your docs folder, e.g. at
:file:`docs/requirements.txt`.

Then, go to your Read the Docs admin panel. Make sure the :guilabel:`Use
virtualenv` checkbox is enabled, and set the :guilabel:`Requirements file`
field to the path to your :file:`requirements.txt` file.

Read the Docs should now build and display your theme correctly, assuming your
:file:`conf.py` contains the changes described above.
