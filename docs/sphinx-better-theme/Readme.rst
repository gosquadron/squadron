A Better Sphinx Theme
---------------------

`Read the documentation`_

`See a demo`_

.. _Read the documentation: https://sphinx-better-theme.readthedocs.org/en/latest/

.. _See a demo: https://sphinx-better-theme.readthedocs.org/en/latest/demos.html

What is this?
^^^^^^^^^^^^^

This is a modified version of the default Sphinx theme with the following
goals:

1. Remove frivolous colors, especially hard-coded ones
2. Improve readability by limiting width and using more whitespace
3. Encourage visual customization through CSS, not themeconf
4. Use semantic markup

v0.1 meets goals one and two. Goal three is partially complete; it's simple to
add your own CSS file without creating a whole new theme. `Open a ticket` if
you'd like something changed.

.. _Open a ticket: https://github.com/irskep/sphinx-better-theme/issues/new

Compatibility
"""""""""""""

sphinx-better-theme is compatible with Sphinx 0.6.4+ and Jinja 2.3.1+. Older
versions may work but have not been tested.

Installation
^^^^^^^^^^^^

Get it from PyPI::

    > pip install sphinx-better-theme

Or `download the zip file`_ and run the usual command::

    > python setup.py install

.. _download the zip file: https://github.com/irskep/sphinx-better-theme/archive/master.zip

Once the package is installed, make these changes to ``conf.py`` to direct
Sphinx to use the theme::

    from better import better_theme_path
    html_theme_path = [better_theme_path]
    html_theme = 'better'
