Getting Started
===============

Squadron configures your service. It install packages, writes out templates, and tests them.

Install Squadron
----------------

First, get the prerequisites::

    $ sudo apt-get install git python python-pip

or, if you're on OS X::

    $ brew install python python-pip git

Now let's install squadron::

    $ sudo pip install squadron

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
deploy a service called apache2 as an example.

To make a service, we need to provide a service version. This isn’t the version
of apache, but instead the version of this deployment configuration::

    $ squadron init-service --service apache2 --version 0.0.1 
    $ tree -F services/apache2
    apache2/
    └── 0.0.1/
        ├── actions.json
        ├── defaults.json
        ├── react.json
        ├── root/
        ├── schema.json
        └── state.json

We won’t need all these files yet, and Squadron gives you sensible defaults if you don’t need the features they provide.

Let’s make a state.json to install apache2 for our Hello Squadron demo::

    { 
        “apt”: [“apache2”]
    }

That’s it! Now when we deploy we will make sure that these two packages are installed to the latest version.

Templating
^^^^^^^^^^
Squadron takes whatever files you have in root/ and deploys them to the correct directory (which in this). Let’s say there’s two files needed to configure metadata-api::

    $ cd services/apache2/0.0.1
    $ tree -F root
    root/
        ├── index.html~tpl
        └── mypage.html

Squadron configures The extension ~tpl means templating will be applied to that file and it will generate a file called index.html. Since mypage.html doesn’t have any extension supported by Squadron, it will just be put in the directory as-is.

Squadron uses the Quik templating library, so index.html~tpl will look something like this::

    <html>
        <body>
            <h1>Squadron works!</h1>
            <p>You’ve deployed the configuration for @company!</p>
            <p>Here’s a port: @port</p>
        </body>
    </html>

@env_type will be replaced by the value in the configuration for that environment.  @port will be replaced by the default value in our service.

Configuration
^^^^^^^^^^^^^

How do all those values get set? They’re set in two ways.

The first is from the service configuration for each environment. Back in the top level of the Squadron directory, there’s a directory called config/. In it are your environments.

Environments are distinct places you can deploy your code to that don’t interact with each other. This allows you to have multiple testing environments that don’t affect your customers. Let’s make a development environment for our apache2 service::

    $ cd -
    $ ls
    config/ services/ nodes/ libraries/
    $ squadron init --env dev

Alright, now we can configure our apache2 service. Let’s write apache2.json in config/dev/::

    {
        "version" : "0.0.1",
        "config" : {
                "company" : "ACME Co."
        },
        "base_dir" : "/var/www"
    }

Most of that was already filled in by squadron init. The "version" field tells Squadron which service description version to use. Different environments can use different service description versions at the same time.

The “config” field is a JSON object that will be given to your service. These fields can be used in templates. If you have config that is often the same between environments, you can put it in another place.

There is a defaults.json file in each service. Let’s make a JSON file that looks like this::

    $ cd ../..
    $ cat service/apache2/0.0.1/defaults.json
    {
        "port":80
    }

If you don’t specify “port” in the apache2.json config file, it will be set to 80 by Squadron. Setting port in the apache2.json file will override this one.

The "base_dir" field tells Squadron where the root/ directory should be written to. Since we’re just deploying files to our web root, it’s /var/www.

Schema
^^^^^^
Squadron includes one very useful file with every service description called schema.json. This is a JSON schema describing the configuration that your service accepts. For our service it looks like this::

    {
        "type" : "object",
        "properties" : {
            "port" : {
                "description" : "a port",
                "type" : "integer",
                "minimum" : 0,
                "maximum" : 65535
            },
            "env_type”: {
                "description" : "what environment type this is",
                "type" : "string",
        },
        "required": ["port", "env_type"]
    }

This allows you to be sure that you passed in the correct types of input in your config files and in your defaults.

Nodes
-----

Now, how can you make sure that each node which runs Squadron runs the correct stuff? That the database node doesn’t install Apache? Enter the nodes directory::

    $ ls
    config/ services/ nodes/ libraries/
    $ cd nodes

This directory should have in it exact domain name matches (FQDN, to be precise) of the machine, or you can use glob style matching with pound (#) being the glob marker, instead of the usual asterisk (*). Files would look like these::

    $ ls
    dev-01.nyc.example.com # Only matches the machine with that name
    dev-#.example.com      # Matches all dev machines
    #-db#.example.com      # Matches all database machines
    #                  # Matches all machines

Node files look like this::

    $ cat #
    {
        "env":"dev",
        "services":["apache2"]
    }

Any node will run apache2 in the dev environment for this example.

Testing your changes locally
----------------------------

We want to make sure that our configuration works as expected. Squadron allows you to see the result of your configuration before even touching a remote server.

Here we will pretend that we are the machine mywebserver.com and see the results locally without modifying our system::

    $ squadron check -n mywebserver.com
    State library actions:
    apt would apply [apache2, git]

    Configuration output has been placed below
    /tmp/squadron/2013-11-14-pfi2/mywebserver/

    $ tree /tmp/squadron/2013-11-14-pfi2/mywebserver/
    -- index.html
    -- mypage.html 

We can now go to index.html and see that our template has been applied::

    <html>
        <body>
            <h1>Squadron works!</h1>
            <p>You’ve deployed the configuration for ACME Co.!</p>
            <p>Here’s a port: 80</p>
        </body>
    </html>

Deploying your changes remotely
-------------------------------

You'll need a git server and then the squadron daemon running on your web server.

Set up git::

    $ git remote origin add your_origin
    $ git add files you changed
    $ git commit # automatically runs squadron check for you!
    $ git push # deploys!

Then set up the daemon::

TODO

It’s really that easy. Any node running the Squadron daemon will pull down your changes over the next 30 minutes.
