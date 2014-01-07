User guide
==========

For installation instructions, see :doc:`installation`.

If you get stuck, you can look for information in Sphinx's documentation for
`using a theme`_, but in theory all the relevant information is collected right
here. `Open a Github issue`_ if something's missing.

This document assumes you've already set up Sphinx and have some docs written.

.. _using a theme: http://sphinx-doc.org/theming.html#using-a-theme
.. _Open a Github issue: https://github.com/irskep/sphinx-better-theme/issues/new

sphinx-better-theme is meant to be customized primarily via CSS. There are a
few options that you can set in :file:`conf.py`, but they are either
functionality-related or appear in more than one annoying-to-type selector.

CSS-based customization is currently limited by the inflexibility of the
markup. That situation should improve over time as sphinx-better-theme sheds
more and more of its inheritance from the basic theme.

Feel free to read `the conf.py for this site`_ to get ideas for your own site.
Make sure you also read :ref:`suggested-sphinx-options`.

.. _the conf.py for this site: https://raw.github.com/irskep/sphinx-better-theme/master/docs/conf.py

Theme options
-------------

Unless you're creating your own theme that inherits from sphinx-better-theme,
you're probably setting theme options in :file:`conf.py`. Here are all the
defaults::

  html_theme_options = {
    # show sidebar on the right instead of on the left
    'rightsidebar': False,

    # inline CSS to insert into the page if you're too lazy to make a
    # separate file
    'inlinecss': '',

    # CSS files to include after all other CSS files
    # (refer to by relative path from conf.py directory, or link to a
    # remote file)
    'cssfiles': ['_static/my_style.css'],  # default is empty list

    # show a big text header with the value of html_title
    'showheader': True,

    # show the breadcrumbs and index|next|previous links at the top of
    # the page
    'showrelbartop': True,
    # same for bottom of the page
    'showrelbarbottom': True,

    # show the self-serving link in the footer
    'linktotheme': True,

    # width of the sidebar. page width is determined by a CSS rule.
    # I prefer to define things in rem because it scales with the
    # global font size rather than pixels or the local font size.
    'sidebarwidth': '15rem',

    # color of all body text
    'textcolor': '#000000',

    # color of all headings (<h1> tags); defaults to the value of
    # textcolor, which is why it's defined here at all.
    'headtextcolor': '',

    # color of text in the footer, including links; defaults to the
    # value of textcolor
    'footertextcolor': '',

    # Google Analytics info
    'ga_ua': '',
    'ga_domain': '',
  }

Adding static files
-------------------

(This is all vanilla Sphinx, but you'll need it for the next section.)

#. Configure a static directory::

    html_static_path = ['_static']

#. Put a file in it (e.g. :file:`docs/_static/cat.png`).

#. Use it.

Using CSS files
---------------

#. Add your CSS file as a static file as above (like
   :file:`docs/_static/style.css`).

#. Add the file name to the ``html_theme_options['cssfiles']`` list in
   :file:`conf.py` (like
   ``html_theme_options['cssfiles'] = ['_static/style.css']``)

You should read `better's CSS files`_ or poke around with your browser's
element inspector to get an idea of what selectors you should override.
:file:`better_basic.css_t` is my fork of the basic theme's CSS, and
:file:`better.css_t` is the stylistic overrides.

.. _better's CSS files: https://github.com/irskep/sphinx-better-theme/tree/master/better/static

Using Javascript files
----------------------

#. Add your Javascript file as a static file as above.

#. Add the file name (relative to the static directory) to the
   ``html_theme_options['scriptfiles']`` list.

.. _suggested-sphinx-options:

Suggested Sphinx options
------------------------

Set ``html_short_title`` to ``"Home"`` so the first breadcrumb says "Home"
instead of your long project title::

    html_short_title = "Home"

`Change your sidebars`_. Since the nav bars have useful "next" and "previous"
links in this theme, you can remove the "Next Topic" and "Previous Topic"
sidebar components. Here's what that looks like::

    html_sidebars = {
        '**': ['localtoc.html', 'sourcelink.html', 'searchbox.html'],
    }

Here are two more custom sidebar components that the `mrjob docs`_ use to
improve usability:

* On the index page, don't include any table of contents in the sidebar.
  Instead, link to commonly used pages.
* Link to the mailing list, or whatever the preferred support channel is for
  your project.

mrjob's config looks like this to support those components::

    html_sidebars = {
        '**': ['localtoc.html', 'sidebarhelp.html', 'sourcelink.html',
               'searchbox.html'],
        'index': ['indexsidebar.html', 'sidebarhelp.html', 'sourcelink.html',
                  'searchbox.html'],
    }

Those HTML files live in `docs/_templates/`_. See `Sphinx's templating guide`_
for more information about how to write them.

.. _Change your sidebars: http://sphinx-doc.org/config.html#confval-html_sidebars
.. _mrjob docs: http://mrjob.readthedocs.org/
.. _docs/_templates/: https://github.com/Yelp/mrjob/tree/master/docs/_templates
.. _Sphinx's templating guide: http://sphinx-doc.org/templating.html
