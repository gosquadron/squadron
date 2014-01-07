Why?
====

* It looks nice.
* It's easy to style with CSS (no :file:`_theme/` directory required).
* The navigation is laid out better.
* It works well on small screens and mobile devices.

If you find sphinx-better-theme lacking in any of these areas, *please* `open a
Github issue`_.

.. _open a Github issue: https://github.com/irskep/sphinx-better-theme/issues/new

It looks nice
-------------

By default, the only colors are the background color, the body text color, and
the link color. Content is separated by layout and whitespace, not background
color changes.

The font defaults are a little more modern. There is less variation in font
styles. Content is wrapped to about 100 characters by default.

Some docs may look better with more liberal use of color. This theme supports
that visual style via CSS rules.

It's easy to style with CSS
---------------------------

Unlike every other Sphinx theme I'm aware of, sphinx-better-theme lets you
customize it with CSS without needing a :file:`_theme/` directory, or anything
beyond a CSS file. And you don't even need that; you can declare inline CSS in
your Sphinx config file.

::

  html_theme_options = {
    'inlinecss': 'color: green;',
    'cssfiles': ['_static/my_style.css'],
  }

One of this project's major goals is to make visual customization easier so
that projects can brand their docs better.

The navigation is laid out better
---------------------------------

The project title is displayed in a header instead of a tiny breadcrumb link.

The links to the next and previous pages in the navigation bars at the top and
bottom use the actual names of the pages instead of the opaque "next" and
"previous". This feature was lifted from the `Guzzle project's docs`_.

.. _Guzzle project's docs: https://github.com/guzzle/guzzle_sphinx_theme

It works well on small screens and mobile devices
-------------------------------------------------

The built-in themes do not work well on small screens. A few other third party
themes get this right, but it's not widespread.

Deficiencies
------------

The markup isn't easy enough to fully customize with CSS. One of the long-term
goals of this project is to make the markup more semantic.

The placement of the logo image isn't good.

`Your idea here <https://github.com/irskep/sphinx-better-theme/issues/new>`_
