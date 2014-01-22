Next steps
===============

Now that you have a basic Squadron setup going, it's time to make it do more
for you.

If you want to follow along with this guide, we've made a git repo for you so
you don't have to type out all these commands.

Just do this and you'll be at the start of the next steps guide (which is the
end of the getting started guide)::

    $ git clone -b simple https://github.com/gosquadron/example-squadron-repo.git

The end result of this page is in the nextsteps branch of the same repo.

Apache configuration
--------------------

Now we want our website to be in PHP. So let's look at what we're starting
with::

    $ tree -F
    .
    |-- config/
    |   |-- dev/
    |   |   `-- website.json
    |   `-- prod/
    |       `-- website.json
    |-- libraries/
    |-- nodes/
    |   |-- dev#
    |   `-- prod#
    `-- services/
        `-- website/
            `-- 0.0.1/
                |-- actions.json
                |-- defaults.json
                |-- react.json
                |-- root/
                |   |-- main~git
                |   `-- robots.txt~tpl
                |-- schema.json
                |-- state.json
                `-- tests/

Okay, so let's make a new dev version of our service::

    $ cp -r services/website/0.0.1 services/website/1.0.0

It's important to use `semantic versioning <http://semver.org/>`_ for your services, as it communicates vital information to the user. This new version will be backwards incompatible. Let's update our dev environment::

    $ cat > config/dev/website.json
    {
        "base_dir": "/",
        "config": {
            "disallow":["/secret/*","/admin/*"],
            "release":"master"
        },
        "version": "1.0.0"
    }

We've changed the `base_dir` to be root because we're going to need to be updating a lot of different paths. We've also increased the version to match our latest version.

New root
^^^^^^^^

Let's make our new root directory::

    $ cd services/website/1.0.0/root
    $ mkdir -p var/www/
    $ mv main~git var/www/
    $ mv robots.txt~tpl var/www/

You can see how this reflects our new `base_dir` of root.

Apache module
^^^^^^^^^^

We also need to make sure that PHP is installed::

    $ cd ..
    $ cat > state.json
    {
            "apt": ["apache2", "libapache2-mod-php5"]
    }

Now we need to run a2enmod when this is installed. We actually need to set up two files for this: `actions.json` and `react.json`.

The file `actions.json` describes the possible actions that can take place. These are commands that are run. Sometimes restarting the service, sometimes starting it. Ours will look like this::

    {
        "run a2enmod php": {
            "commands": ["a2enmod php5", "/etc/init.d/apache2 restart"],
        },
        "start" : {
            "commands" : ["/etc/init.d/apache2 start"]
        },
        "reload" : {
            "commands" : ["/etc/init.d/apache2 reload"],
            "not_after" : ["start", "restart"]
        },
        "restart" : {
            "commands" : ["/etc/init.d/apache2 restart"],
            "not_after" : ["start"]
        }
    }

So we have four actions. Three are easy enough to understand: they control the running of the service. Starting apache, reloading it, and restarting it. The `not_after` property means that if there are several actions to run for a deployment, that these should not be run after successful invocations of those. This will be more clear after understanding `react.json`.

The file `react.json` describes how to react to various events. It gives criteria for the events and then which actions to execute. Ours looks like this::

    [
        {
            "execute": ["run a2enmod php"],
            "when" : {
                "not_exist": "/etc/apache2/mods-enabled/php5"
            }
        },
        {
            "execute": ["start"],
            "when" : {
                "command": "/etc/init.d/apache2 status",
                "exitcode_not": 0
            }
        },
        {
            "execute" : ["reload"],
            "when" : {
                "files" : ["*.conf", "*/conf.d/*"]
            }
        }
    ]


