.. _overview:

Overview
========

Squadron helps you deploy and configure your software. It grabs your software,
sets it up right, starts it up, and has built-in tests to make sure this goes
off without a hitch.

Squadron is good for:

* Deploying complex websites
* Releasing your new software-as-a-service application
* Deploying testing and production versions of your code
* Testing your configuration

The basic process of using Squadron is: make a Squadron repo, configure your 
service after learning how Squadron works, commit your changes, and then run 
`squadron` on your servers.

Features
--------

Squadron has a bunch of features to help you download, configure, and test your
software and its dependencies.

Multiple ways to get your code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With Squadron, you can download binaries, download tarballs of your code, grab
your source with git.  With `apt`, `virtualenv`, and `npm` support, you can get 
your code's dependencies.

After grabbing your code, Squadron can run :ref:`test` and use :ref:`atomic` to 
deploy your code.

Easy dependency management
^^^^^^^^^^^^^^^^^^^^^^^^^^

Squadron supports apt, npm, and pip via virtualenv, and we're always adding
more. Adding a new package to install is super easy, and you can have different
packages in different :ref:`env`.

Easy Templating
^^^^^^^^^^^^^^^

Squadron uses a simple templating library called `Quik
<https://github.com/avelino/quik>`_ to write configuration templates. They look
like this::

    [log]
    debuglog = @loglevel rotatinglog @logdir 5000 5
    #if @output:
    outputlog = DEBUG stderr
    #end

This is used to write out your configuration files for your software. Values
are set through defaults and service configurations and can be different for
different :ref:`env`.

.. _atomic:

Atomic Deployments
^^^^^^^^^^^^^^^^^^

Did you know that deploying your code takes time? And during that time your
users might get inconsistent results? Why bother with that headache. Deploy
your code atomically!

Squadron can easily deploy your code atomically via a symlink so that its
either all the new version or doesn't reflect any changes at all.

.. _env:
 
Environments
^^^^^^^^^^^^

You want to have a development and production environments? Easy. You want to
have six different QA environments? Done. You need two production environments
for A/B testing? Trivial.

Environments are easy with Squadron.

.. _test:

Built-in Tests
^^^^^^^^^^^^^^

Squadron has two types of built-in tests: automatic tests you don't have to
write, and an easy framework for testing your deployed code.

If you write a JSON file as part of a template, Squadron will check to make
sure it's a valid JSON file. In the future, XML files written out by templates
will be similarly checked, and if they have a schema, that will be verified.

The second type of tests are the kind you write because you know your service.
Do you write a PHP script to hit a URL? Or a simple bash script to check if
your service is running? Whatever you want, we'll run it.

Rollback
^^^^^^^^

What if your deployment goes wrong?

With traditional configuration management software, it's difficult or
impossible to rollback to exactly how it was before the deployment. With
Squadron, that's built-in.

No programming
^^^^^^^^^^^^^^

And, maybe best of all, there's no programming involved. There's no `Domain
Specific Language <http://en.wikipedia.org/wiki/Domain-specific_language>`_ to
learn. It's all just config that is rigorously checked by Squadron when you run
it.

No programming means less testing and little to no debugging so you can get
what you want done faster and easier.

Open source
-----------

Squadron is open source software written in Python. 
`Our project source and issue tracker is on Github 
<https://github.com/gosquadron/squadron>`_. If you'd like to contribute, please
do!

You can get in touch with us via `email <mailto:info@gosquadron.com>`_, on
`Twitter <https://twitter.com/GoSquadron>`_ or via IRC::

    irc.freenode.net #squadron

We'd love to hear from you!

Sound good?
-----------

Does it sound like Squadron fits your use case? If so, head on over to the 
:ref:`getstarted` section and try Squadron out!
