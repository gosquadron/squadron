User Guide
==========

This is a reference guide to the various components of Squadron.

Extensions
----------

Extensions are used in the root directory of a service to do some kind of
transformation on them.

dir
^^^

The 'dir' extension creates an empty directory of that name.

**Contents**

None

download
^^^^^^^^

The 'download' extension downloads a file over HTTP.

**Contents**

A single line of the HTTP endpoint with an optional SHA256 prefix hash of the 
file. Will have a template applied to it, so variable substitution and logic 
is possible.

Examples::

    http://www.example.com/filename.ext a7898bc

or::

    http://no.sha256.here.com/file.to.download.txt

git
^^^

The 'git' extension clones git repositories.

**Contents**

A single line, with the git remote and an optional refspec, seperated by a
space. Will have a template applied to it, so variable substitution and logic
is possible.

Examples::

    https://github.com/gosquadron/squadron.git  master

or::

    git@github.com:gosquadron/example-squadron-repo.git

tpl
^^^
The template extension simply applies a template to the given file.

**Contents**

The template is the content.

Example::

    <html>
        <body>
            <h1>Hello, @user!</h1>
    #for @p in @paragraphs:
            <p>@p</p>
    #end
        </body>
    </html>

virtualenv
^^^^^^^^^^

Creates a Python `virtualenv <http://www.virtualenv.org>`_. The virtualenv and
`pip <http://www.pip-installer.org>`_ commands must be available and in the 
current user's PATH. Run through a template so variable substitution is
possible.

**Contents**

The contents of this file are passed to pip as if they were a requirements.txt
file.

Example::

    Flask==@versions.flask
    Jinja2==2.6
    Werkzeug==0.8.3
    certifi==0.0.8
    chardet==1.0.1
    distribute==0.6.24
    gunicorn==0.14.2
    requests==0.11.1


Libraries
---------

Libraries are Python modules which are applied through `state.json`.

How to write a library
^^^^^^^^^^^^^^^^^^^^^^

In the `libraries` directory of your Squadron repository, you can place a
Python module.

The Python module should expose three functions::

    def schema():
        return {}

    def verify(inputhashes):
        return []

    def apply(inputhashes, dry_run=True):
        return []

The schema function should return the Python representation of a `JSON schema
<http://json-schema.org>`_. It describes one object passed into the verify
function.

The verify function takes a list of objects (of the type described in the
schema). It then returns a list of objects that are not already in the state
specified.

The apply function takes the list of objects that failed verification (weren't
yet in the state they were supposed to be in) and a boolean dry_run. It returns
a list of objects that couldn't be applied.

Included libraries
^^^^^^^^^^^^^^^^^^

Some libraries are included with Squadron so you don't have to write them
yourself.

apt
"""

Installs packages via apt. Takes a list of string names, each string is a
package to be installed via apt.

Action and reaction
-------------------

To perform actions when certain files are created or modified such as restart a
service or run a command, you need to first create an action and then create a
reaction to trigger it.

Actions
^^^^^^^

Actions are described in `actions.json` in each service. An action has a name,
a list of commands to run, and a list of actions to not run this one after.

Here's what one might look like::

    {
        "start" : {
            "commands" : ["/etc/init.d/service start"]
        },
        "reload" : {
            "commands" : ["killall -HUP service"],
            "not_after" : ["start", "restart"]
        },
        "restart" : {
            "commands" : ["/etc/init.d/service restart"],
            "not_after" : ["start"]
        }
    } 

So this service has three actions. The `start` command starts up the service.
The `restart` command restarts it, but only if the `start` command didn't just
succeed. This way you can avoid restarting a service immediately after starting
it.

Reactions
^^^^^^^^^

Reaction trigger actions in this service or other services based on files
being created or modified. The reactions are described in `react.json` in each
service.

One might look like this::

    [
        {
            "execute": ["start", "apache2.restart"],
            "when" : {
                "command": "pidof service",
                "exitcode": 1
            }
        },
        {
            "execute" : ["restart"],
            "when" : {
                "files" : ["mods-enabled/*"]
            }
        },
        {
            "execute" : ["reload"],
            "when" : {
                "files" : ["*.conf", "conf.d/*"]
            }
        }
    ]

The first reaction starts this service and restarts another service called 
`apache2` when it's not running.

The second reaction restarts this service if there are any modules created or
modified. You can use 'files-created' or 'files-modified' to narrow this scope.

The third reaction reloads this service when any of the config files change.

The executing actions must be defined in `actions.json` or an error will be
raised.

Tests
-----

Testing is an important part of configuring software. Tests live in the `tests`
directory of each service.

After the service is configured, applied, and the reactions trigger the
actions, all executable files in this directory are run.

On standard input, a JSON string is provided which describes the various
configuration options for this service. It looks like this::

    {
        "version": "0.0.1", 
        "config": {
            "debug": false,
            "workers": 100
        },
        "atomic": {}, 
        "dir": "/var/squadrontmp/sq-0/service", 
        "base_dir": "/var/service/"
    }

The test *must* read standard input even if it does not intend to use this
information.

Returning a non-zero status code indicates a test failure.
