Next steps
===============

Now that you have a basic Squadron setup going, it's time to make it do more
for you.

If you want to follow along with this guide, we've made a git repo for you so
you don't have to type out all these commands.

Just do this and you'll be at the start of the next steps guide (which is the
end of the getting started guide)::

    $ git clone -b simple2 https://github.com/gosquadron/example-squadron-repo.git

The end result of this page is in the `nextsteps2` branch of the same repo.

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
    |   |-- dev%
    |   `-- prod%
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

You can see how this reflects our new `base_dir` of root. It would also be nice
if we released our web root atomically so that if anyone happens to load it
while we're copying over, they don't get half new and half old assets.
Fortunately, this is really easy with Squadron::

    $ cat > config.sq
    var/www/ atomic:true user:nobody group:nobody

The `config.sq` file in the `root` directory of a service is special. It's not
copied to your `base_dir`, but instead configures some metadata, such as
setting the user, group, or mode for a file or directory. For more information,
see the :ref:`configsq` section of the :ref:`userguide`.

What we've done here is to tell Squadron to do an atomic deploy of `var/www/`,
which means it will use a symbolic link from /var/www/ to Squadron's deployment
directory.

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

For a complete description of actions and reactions, see :ref:`actionreaction` 
in the :ref:`userguide`.

Let's do it::

    $ sudo squadron apply -n dev
    Staging directory: /var/squadron/tmp/sq-8
    Processing apache2, libapache2-mod-php5 through apt
    Applying changes
    Running action website.run a2enmod php in reaction {u'execute': [u'website.run a2enmod php'], u'when': {u'not_exist': [u'/etc/apache2/mods-enabled/php5']}}
    Module php5 already enabled
    * Restarting web server apache2
        apache2: Could not reliably determine the server's fully qualified domain name, using 127.0.1.1 for ServerName
    ... waiting apache2: Could not reliably determine the server's fully qualified domain name, using 127.0.1.1 for ServerName   [ OK ]
    Apache2 is running (pid 2332).
    Successfully deployed to /var/squadron/tmp/sq-8
    ===============
    Paths changed:

    New paths:
        website/var/www/main/LICENSE
        website/var/www/main/index.html
        website/var/www/main/README.md
        website/var/www/robots.txt
    $ ls -l /var/www
    lrwxrwxrwx 1 root root 39 Jan 01 00:00 /var/www -> /var/squadron/tmp/sq-8/website/var/www/

And navigating to http://localhost works!

Testing
^^^^^^^

An important part of deploying software is making sure it's correct. For our
purposes, we want to check that PHP is working and that Apache was set up
correctly.

In Squadron, :ref:`tests` are located in the service's `tests` directory. Let's
make one now::

    $ mkdir -p services/website/1.0.0/tests
    $ cat > services/website/1.0.0/tests/check_php.sh
    #!/bin/bash
                            
    while read line; do
        true
    done

    OUTPUT=`curl http://localhost/main/test.php 2>/dev/null`

    if [ "$?" -eq "0" ]; then  
        if [[ $OUTPUT == *php* ]]; then
            echo "PHP not enabled"
            exit 1
        fi
    else
        echo "Couldn't connect"
        exit 1
    fi

Tests must read in the JSON object passed via standard in. For our test, we
don't care about the configuration, so we just throw it away.

We then test that the connection worked via the exit code flag `$?`. If curl
was successful, we check to make sure the output didn't have the string "php"
in it, which would indicate that PHP wasn't configured properly.

Almost done. We just need to make sure this test is executable and that curl is
installed::

    $ chmod +x services/website/1.0.0/tests/check_php.sh
    $ cat > services/website/1.0.0/state.json
    {
        "apt": ["apache2", "libapache2-mod-php5", "curl"]
    }

And now we're done. Let's run it::

    $ sudo squadron apply -n dev
    Staging directory: /var/squadron/tmp/sq-11
    Processing apache2, libapache2-mod-php5, curl through apt
    Running 1 tests for website v1.0.0
    Nothing changed.

Keeping state between runs
--------------------------

Squadron keeps a file in the state directory (`/var/squadron/info.json` for 
some nodes) which describes what the last successful run did. Here is the 
`info.json` file from our last run::

    {
      "commit":{
        "website":{
          "version":"1.0.0",
          "config":{
            "release":"master",
            "disallow":[
              "/secret/*",
              "/admin/*"
            ]
          },
          "atomic":{
            "var/www/":true
          },
          "dir":"/var/squadron/tmp/sq-8/website",
          "base_dir":"/"
        }
      },
      "dir":"/var/squadron/tmp/sq-8",
      "checksum":{
        "website/var/www/main/LICENSE":"3d8f45ba8ca6ebf6e9990f580df8387d49f3e72e9119ff19e63393c12d236aff",
        "website/var/www/main/index.html":"f680e220f5e58408b233b700d0106b70582765937ca983e7969fd9b66dee599e",
        "website/var/www/main/README.md":"0b3b1635d69e0e501e82d9ec70d15d650f17febc4ea3d4a47adbd07a6025a739",
        "website/var/www/robots.txt":"1bb88650e0ac17db58a556033c0e9cda3534902f8c9cef87ffa8ac4ca6e0635f"
      }
    }

The `commit` block describes what was committed. It is a dictionary of all 
services, what version was deployed, and what configuration was used. We can 
see that we deployed version 1.0.0 of our website service description, with 
the expected configuration. It's also shown that `var/www/` was deployed 
atomically.

There is also a checksum dictionary which keeps the SHA-256 sum of each file it
deploys. If Squadron notices that one of the next run's files has a different
SHA-256 sum, it will replace it.

If we try to rerun Squadron it won't reapply anything because nothing tracked
by Squadron is different::

    $ !sudo
    sudo squadron apply -n dev
    Staging directory: /var/squadron/tmp/sq-9
    Processing apache2, libapache2-mod-php5 through apt
    Nothing changed.

You can grab the completed example for this section by checking out the
nextsteps2 branch from the example repo::

    $ git clone -b nextsteps2 https://github.com/gosquadron/example-squadron-repo.git


Where to go from here
---------------------

The :ref:`userguide` describes all of the functionality of Squadron. If you're
looking for more extension handlers or more state libraries, that's the place
to go. You could even write your own.
