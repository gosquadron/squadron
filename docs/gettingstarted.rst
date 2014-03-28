.. _getstarted:

Getting Started
===============

Squadron configures your software service. It install packages, writes out 
configuration templates, and tests them. This getting started guide tells you
how to do all that. If you'd like to know more about what Squadron can do, 
see the :ref:`overview` of Squadron.

If you want to follow along with this guide, we've made a git repo for you so
you don't have to type out all these commands::

    $ git clone -b simple2 https://github.com/gosquadron/example-squadron-repo.git

You can also play with a `Vagrant box we made 
<https://dl.dropboxusercontent.com/u/10188833/squadron-0.4.1-i686.box>`_
to test out Squadron.

Install Squadron
----------------

First, get the prerequisites::

    $ sudo apt-get install git python python-pip

or, if you're on OS X::

    $ brew install python python-pip git

Now let's install squadron::

    $ pip install squadron
    $ squadron setup
    Location for config [/home/user/.squadron]: 
    Location for state [/home/user/.squadron/state]: 
    Initializing config dir /home/user/.squadron
    Initializing state dir /home/user/.squadron/state

Squadron can be installed into a virtualenv. It uses a directory to store 
:ref:`global-configuration` and another one to store the state change of your 
services. 

Squadron looks for config in the following places:

* /etc/squadron/config
* /usr/local/etc/squadron/config
* ~/.squadron/config
* or in .squadron/config in the Squadron repository itself

From there it reads the location of its state directory. The setup step is
optional if you want to keep the config in the repository and make the state
directory on your own.

Start a Squadron repository
---------------------------

It's not too hard::

    $ mkdir squadron
    $ cd squadron
    $ squadron init
    $ ls
    config/ services/ nodes/ libraries/
    $ git rev-parse --is-inside-work-tree
    true

Squadron uses git for everything, so squadron init automatically makes a git repository for you!

Describe your service
---------------------

So, to deploy a service, you need to tell Squadron how to do it. We’re going to
deploy a simple website as an example.

To make a service, we need to provide a service version. This isn’t the version
of our website, but instead the version of this deployment configuration::

    $ squadron init --service website --version 0.0.1
    $ tree -F services/website
    website/
    `-- 0.0.1/
        |-- actions.json
        |-- copy.json
        |-- defaults.json
        |-- react.json
        |-- root/
        |-- schema.json
        |-- state.json
        `-- tests/

We won’t need all these files yet, and Squadron gives you sensible defaults if you don’t need the features they provide.

Let’s make a state.json to install apache2 for our simple website::

    [ 
        {
            "name":"apt", 
            "parameters":["apache2"]
        }
    ]

Now when we later run squadron, it'll make sure that Apache is installed via
apt-get.

Templating
^^^^^^^^^^
Squadron takes whatever files you have in root/ and deploys them to the correct directory (which in this)::

    $ cd services/website/0.0.1
    $ tree -F root
    root/
        ├── main~git
        └── robots.txt~tpl

So we've got two strange looking filenames. The tilde (~) means that Squadron
will apply that handler to that file. The '~tpl' extension is how you make
files via a template.

Squadron uses the `Quik <http://quik.readthedocs.org/en/latest/>`_ templating library, so robots.txt~tpl will look
something like this::

    User-agent: *
    #for @d in @disallow:
    Disallow: @d
    #end
    Allow: /humans.txt

So the variable @disallow, which is an array, is looped over and so there are
as many Disallow directives as elements in the array.

main~git looks like this::

    {
        "url":"https://github.com/cxxr/example-squadron-repo.git",
        "refspec":"@release"
    }

Squadron will clone this repo when it runs, checkout the refspec simple (which
is a branch, a tag, or a hash) and place it in the 'main' directory. The
variable '@release' will be replaced by whatever we set that to later

Configuration
^^^^^^^^^^^^^

How do all those values get set? They’re set in two ways.

The first is from the service configuration for each environment. Back in the top level of the Squadron directory, there’s a directory called config/. In it are your environments.

Environments are distinct places you can deploy your code to that don’t interact with each other. This allows you to have multiple testing environments that don’t affect your customers. Let’s make a development environment for our website::

    $ cd -
    $ ls
    config/ services/ nodes/ libraries/
    $ squadron init --env dev

Now there's a file called config/dev/website.json, which is prepopulated with
the latest version number. Let's add the disallow config so the file looks like
this::

    {
        "base_dir": "/var/www",
        "config": {
            "disallow":["/secret/*","/admin/*"],
            "release":"master"
        },
        "version": "0.0.1"
    }

The "version" field tells Squadron which service description version to use. Different environments can use different service description versions at the same time.

The “config” field is a JSON object that will be given to your service. These fields can be used in templates. If you have config that is often the same between environments, you can put it in another place.

The "base_dir" field tells Squadron where the root/ directory should be written to. Since we’re just deploying files to our web root, it’s /var/www.

The second way in which these values are set is via defaults.json. This file
can be used to set default values in case none are set. Keys are the key in
question, and the values are the values you would set in the config.

An equivalent defaults.json for our website would be::
    
    {
        "disallow":["/secret/*","/admin/*"]
    }

Schema
^^^^^^
Squadron includes one very useful file with every service description called services/website/0.0.1/schema.json. This is a `JSON schema`_ describing the configuration that your service accepts. For our service it looks like this::

    {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type" : "object",
        "properties" : {
            "disallow" : {
                "description" : "a list of disallow directives",
                "type" : "array",
                "items": {
                    "type": "string"
                },
                "uniqueItems": true
            },
            "release" : {
                "description" : "what to checkout from the git repository",
                "type" : "string"
            }
        },
        "required": ["disallow", "release"]
    }

This allows you to be sure that you passed in the correct types of input in your config files and in your defaults. If you don't supply a JSON Schema, everything will still work, but it won't be checked, either.

You can do some fairly advanced things with JSON Schema, such as regular
expression matching. With this you could ensure that "release" met some tag
pattern or similar.

.. _JSON Schema: http://json-schema.org/

Nodes
-----

Now, how can you make sure that each node which runs Squadron runs the correct stuff? That the database node doesn’t install Apache? Enter the nodes directory::

    $ ls
    config/ services/ nodes/ libraries/
    $ cd nodes

This directory should have in it exact domain name matches (FQDN, to be precise) of the machine, or you can use glob style matching with percent (%) being the glob marker, instead of the usual asterisk (*). Files would look like these::

    $ ls
    dev-01.nyc.example.com # Only matches the machine with that name
    dev-%.example.com      # Matches all dev machines
    %-db%.example.com      # Matches all database machines
    %                      # Matches all machines

Node files look like this::

    $ cat %
    {
        "env":"dev",
        "services":["website"]
    }

Any node will run website in the dev environment unless overridden by another,
more specific node file. All node files that match are sorted by length
ascending, and applied in that order.

Testing your changes locally
----------------------------

We want to make sure that our configuration works as expected. Squadron allows you to see the result of your configuration before even touching a remote server.

Here we will pretend that we are the machine mywebserver.com and see the results locally without modifying our system::

    $ squadron check
    Staging directory: /tmp/squadron-s70Rjh
    Would process apache2 through apt
    Dry run changes
    ===============
    Paths changed:

    New paths:
        website/robots.txt
        website/main/LICENSE
        website/main/README.md
        website/main/index.html

    $ tree -F /tmp/squadron-s70Rjh
    /tmp/squadron-s70Rjh
    `-- website/
        |-- main/
        |   |-- index.html
        |   |-- LICENSE
        |   `-- README.md
        `-- robots.txt

Our template was applied as well::

    $ cat /tmp/squadron-s70Rjh/website/robots.txt
    User-agent: *

    Disallow: /secret/*

    Disallow: /admin/*
    Allow: /humans.txt


Deploying your changes (locally)
--------------------------------

Now, if the machine you're developing on is the machine you'd like to set up
your website on (which is unlikely), you can just apply your changes::

    $ sudo squadron apply
    Staging directory: /var/squadron/tmp/sq-0
    Processing apache2 through apt
    Applying changes
    Successfully deployed to /var/squadron/tmp/sq-0
    ===============
    Paths changed:

    New paths:
        website/main/README.md
        website/robots.txt
        website/main/index.html
        website/main/LICENSE

And you can see that this won't work twice in a row, as nothing has changed::

    $ sudo squadron apply
    Staging directory: /var/squadron/tmp/sq-1
    Processing apache2 through apt
    Nothing changed.

Notice how the staging directory was increased by one. This lets you have
several staged (but not deployed) versions in case of test or deployment 
failures. This is also how auto-rollback works.

Running squadron check produces similar results::

    $ squadron check
    Staging directory: /tmp/squadron-H1Vym2
    Would process apache2 through apt
    Nothing changed.

Deploying your changes (remotely)
---------------------------------

Squadron will work regardless of how you get your files to your remote servers.
If you SCP them over each time and then run squadron apply, it'll work, but
that's not very convenient. 

The standard way is polling the git repository.

You'll need a git server and then the squadron daemon running on your web server.

Set up git::

    $ git remote origin add your_origin
    $ git add files you changed
    $ git commit # automatically runs squadron check for you!
    $ git push # deploys!

Then set up the daemon::

    $ squadron daemon

It’s really that easy. Any node running the Squadron daemon will pull down your changes over the next 30 seconds.

You can configure the poll interval and logging for the daemon using the system
config file described in :ref:`global-configuration`.

More environments
-----------------

Now that you've tested your website in your development environment, it's time for it to go to production::

    $ squadron init --env prod --copyfrom dev
    Initialized environment prod copied from dev

This is another way to initialize environments. It copies all the config from the dev environment to the prod environment. Now we have this in `config`::

    $ tree -F config
    config/
    |-- dev
    |   `-- website.json
    `-- prod
        `-- website.json
    $ diff -u config/dev/website.json config/prod/website.json
    $

No differences because they're the same!

Let's change our nodes so that nodes can choose to be dev or production::

    $ cd nodes
    $ mv % dev%
    $ cat > prod%
    {                     
        "env":"prod",      
        "services":["website"]
    }

Any node whose name begins with dev will get the dev environment, while any node that begins with prod will get the prod environment. This allows you to test your changes before making them live.
