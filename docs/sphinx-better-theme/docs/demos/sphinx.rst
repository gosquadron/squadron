Sphinx style demo
=================

See :doc:`../index` for the table of contents. Reproducing it here would
make Sphinx mad.

Feel free to open Github issues about the specifics of the styles on this page.

Paragraph-level markup
----------------------

note, warning
^^^^^^^^^^^^^

.. note:: This is a note. It can have ``monospaced text``.

.. warning:: This is a note. ``monospaced text``.

versionadded, deprecated
^^^^^^^^^^^^^^^^^^^^^^^^

.. versionadded:: 0.1
    Some stuff added in a version.

.. deprecated:: 0.1
    Some stuff deprecated in a version.

seealso
^^^^^^^

.. seealso::

    `mrjob <http://pythonhosted.org/mrjob>`_
        Another awesome open source project

    `Buildy <http://playbuildy.com>`_
        A cool online game

rubric
^^^^^^

.. rubric:: A paragraph heading that is not used to create a TOC node

centered
^^^^^^^^

.. centered:: LICENSE AGREEMENT

hlist
^^^^^

.. hlist::
    :columns: 3

    * A list of
    * short items
    * that should be
    * displayed
    * horizontally

Misc
----

glossary
^^^^^^^^

.. glossary::

    glossary
        A directive that contains a definition list with terms and definitions.
        The definitions will then be referencable with the ``term`` role.

    term
        A string defined in the glossary.

Here we reference the :term:`glossary` term.

productionlist
^^^^^^^^^^^^^^

.. productionlist::
   try_stmt: try1_stmt | try2_stmt
   try1_stmt: "try" ":" `suite`
            : ("except" [`expression` ["," `target`]] ":" `suite`)+
            : ["else" ":" `suite`]
            : ["finally" ":" `suite`]
   try2_stmt: "try" ":" `suite`
            : "finally" ":" `suite`

Showing code examples
---------------------

Double colon
^^^^^^^^^^^^

Here is some unhighlighted code::

    old pond...
    a frog leaps in
    water’s sound

code-block
^^^^^^^^^^

Line numbers with the second line emphasized:

.. code-block:: python
    :linenos:
    :emphasize-lines: 2

    if True:
        print "This is some Python"

No line numbers:

.. code-block:: python

    if True:
        print "This is some Python"

Tables
^^^^^^

======= === === =====
This    is  a   table
======= === === =====
1       2   3   4
5       6   7   8
======= === === =====


Inline markup
-------------

.. _my-reference-label:

References
^^^^^^^^^^

:ref:`A link to the above heading <my-reference-label>`

:doc:`A link to the index document <../index>`

:download:`Download this demo (demo.rst) <sphinx.rst>`

:envvar:`ENV_VAR`

:token:`token`

.. option:: --option <option>

    Description of option.

:option:`--option`, :option:`--option-without-ref`

:term:`term` (see :ref:`Glossary` for an example with a link)

Other semantic markup
^^^^^^^^^^^^^^^^^^^^^

:abbr:`abbr (an abbreviation)` (hover)

:command:`command` is an OS-level command.

:dfn:`dfn` is the defining instance of a term in the text.

:file:`/a/file/path/{variable}/more`

:guilabel:`GUI control label`

:kbd:`Control-x Control-f` (keystroke sequence)

:mailheader:`Content-Type` (mail header)

:makevar:`MAKE_VAR`

:manpage:`manpage(1)`

:menuselection:`Menu --> Selection`

:mimetype:`mime/type`

:newsgroup:`Usenet newsgroup (wat?)`

:program:`Name of an executable program` (not just ``:command:`` for some
reason?)

:regexp:`unquoted?regular*[expression]`

:samp:`A piece of literal text with {variables}`

:pep:`8`

:rfc:`1072`

Substitutions
^^^^^^^^^^^^^

Release |release|, version |version|, today |today|

Python
------

:py:mod:`py_module`

.. py:function:: py_func(arg, a_long_argument=with_a_default, foo=bar, baz=qux, more=more, args=args, for=for, wrapping=wrapping)

    A Python function definition.

:py:func:`py_func`, :py:func:`py_func_no_ref`

.. py:class:: PyClass(arg)

    .. py:method:: py_method(arg)

:py:class:`PyClass`, :py:class:`PyClassNoRef`, :py:meth:`PyClass.py_method`,
:py:meth:`py_method_no_ref`
