.. _userguide:

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

extract
^^^^^^^

The 'extract' extension downloads and extracts tarballs and zip files.

**Contents**

The extract extension handler takes a JSON object like this::

    {
        "url": "http://www.example.com/dir/file.tar.bz2"
    }

or with manually specifying the type::

    {
        "url": "https://www.example.com/dir/filename_without_ext",
        "type": "tar.gz"
    }

The extract handler can also copy files out of the tarball::

    {
        "url": "https://www.example.com/dir/file.zip",
        "persist": false,
        "copy": [
            {
                "from": "test*",
                "to": "/etc/test/"
            },
            {
                "from": "dir/file.txt",
                "to": "../file.txt"
            }
        ]
    }

The full list of supported fields is described in the following table.

+------------------+----------------------------------------------+
| **Name**         | **Description**                              |
+------------------+----------------------------------------------+
| url              | URL to download the tarball from. Required.  |
+------------------+----------------------------------------------+
| type             | One of "tar.gz", "tar", "tar.bz2", or "zip". |
|                  | Optional if it can be inferred from filename.|
+------------------+----------------------------------------------+
| persist          | Whether or not to keep around the directory  |
|                  | specified by this extension handler. If      |
|                  | false, it should be used with copy, as       |
|                  | non-copied files will be unavailable.        |
|                  | Defaults to true.                            |
+------------------+----------------------------------------------+
| copy             | An array of copy objects, described in the   |
|                  | following table.                             |
+------------------+----------------------------------------------+

The copy objects are described in the following table.

+------------------+----------------------------------------------+
| **Name**         | **Description**                              |
+------------------+----------------------------------------------+
| from             | A glob match which matches files based on the|
|                  | path relative to the tarball.                |
+------------------+----------------------------------------------+
| to               | The destination to copy the files to. If it's|
|                  | an absolute path, it copies it there. If it's|
|                  | a relative path, it's relative to the        |
|                  | directory that would have been created by the|
|                  | extension handler if persist was true. Does  |
|                  | not create directories.                      |
+------------------+----------------------------------------------+

git
^^^

The 'git' extension clones git repositories.

**Contents**

A JSON object with properties such as "url". Will have a template applied to it, so variable substitution and logic is 
possible.

Examples::

    {
        "url":"https://github.com/gosquadron/squadron.git"
    }

or::

    {
        "url":"git@github.com:gosquadron/example-squadron-repo.git",
        "refspec":"experimental"
    }

or even::

    {
        "url":"git@github.com:gosquadron/example-squadron-repo.git",
        "refspec":"@release",
        "sshkey":"ssh_keys/deploy1",
        "args":"--depth=2"
    }

The last example requires that the `ssh_keys/deploy1` resource exists and is a
private ssh key. See the :ref:`resources` section for more information. It also
does a shallow clone of the git repository via the --depth argument.

The properties allowed in the object are described in the following table:

+------------------+----------------------------------------------+
| **Name**         | **Description**                              |
+------------------+----------------------------------------------+
| url              | URL to clone the git clone from. Required.   |
+------------------+----------------------------------------------+
| refspec          | The branch, tag, or commit hash to checkout  |
|                  | after clone. Optional.                       |
+------------------+----------------------------------------------+
| sshkey           | Relative path to the sshkey resource. See the|
|                  | :ref:`resources` section for more            |
|                  | information. Optional.                       |
+------------------+----------------------------------------------+
| args             | Command line arguments to pass to git clone. |
|                  | Optional.                                    |
+------------------+----------------------------------------------+

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

Example state.json with apt::

    {
        "apt": ["screen","tmux"]
    }

group
""""

Creates groups. Takes an object with the following fields.

+--------------+---------------------------+
| **Field**    | **Description**           |
+----------+---+---------------------------+
| name     | Required. Sets the group name |
+----------+-------------------------------+
| gid      | Integer. Specific group id    |
+----------+-------------------------------+
| system   | Boolean. Is a system group?   |
+----------+-------------------------------+

Example state.json with group::

    {
        "group": [
            {
                "name": "newgroup"
            },
            {
                "name": "specificgroup",
                "gid": 555,
                "system": true
            }
        ]
    }

user
""""

Creates users. Takes an object with the following fields.

+--------------+--------------------------+
| **Field**    | **Description**          |
+----------+---+--------------------------+
| username | Required. Sets the user name |
+----------+------------------------------+
| shell    | User's command shell         |
+----------+------------------------------+
| realname | User's real name             |
+----------+------------------------------+
| homedir  | User's home directory        |
+----------+------------------------------+
| uid      | Integer. Specific user id    |
+----------+------------------------------+
| gid      | Integer. Specific group id   |
+----------+------------------------------+
| system   | Boolean. Is a system user?   |
+----------+------------------------------+

Example state.json with user::

    {
        "user": [
            {
                "username": "newuser"
            },
            {
                "username": "specificuser",
                "shell":"/bin/bash",
                "homedir":"/users/specificuser"
                "realname":"Specific User"
            },
            {
                "username":"windows",
                "uid":666,
                "system":true
            }
        ]
    }

.. _actionreaction:

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

Here are the possible fields to put in an action:

+-----------+-----------------------------------------+
| **Field** | **Description**                         |
+-----------+-----------------------------------------+
| commands  | Required. A list of commands to run     |
+-----------+-----------------------------------------+
| not_after | A list of actions to not run this after |
+-----------+-----------------------------------------+

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
                "exitcode_not": 0
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

Here is a list of fields the top level reaction object can contain:

+-----------+-------------------------------------------------+
| **Field** | **Description**                                 |
+-----------+-------------------------------------------------+
| execute   | Required. A list of actions to run              |
+-----------+-------------------------------------------------+
| when      | Required. An object with fields described below |
+-----------+-------------------------------------------------+

Here is a list of fields that a `when` object can contain:

+----------------+------------------------------------------------------------------------------------+
| **Field**      | **Description**                                                                    |
+----------------+------------------------------------------------------------------------------------+
| command        | Command to run, used with exitcode_not                                             |
+----------------+------------------------------------------------------------------------------------+
| exitcode_not   | Run action if exit code for command isn't this                                     |
+----------------+------------------------------------------------------------------------------------+
| files          | List. Run if any of these files were created or modified by Squadron. Can be globs |
+----------------+------------------------------------------------------------------------------------+
| files_created  | List. Run if any of these files were created by Squadron. Can be globs             |
+----------------+------------------------------------------------------------------------------------+
| files_modified | List. Run if any of these files were modified by Squadron. Can be globs            |
+----------------+------------------------------------------------------------------------------------+
| always         | Boolean. Whether or not to always run. Default: false                              |
+----------------+------------------------------------------------------------------------------------+
| not_exist      | List of globs/absolute paths to run if these files don't exist                     |
+----------------+------------------------------------------------------------------------------------+

.. _resources:

Resources
---------

Resources are files that are available to multiple services, such as ssh
private keys, which allow Squadron to deploy software from a private git
server.

Resources are located in the `resources` directory at the top level of
Squadron::

    $ ls -1F
    config/
    nodes/
    resources/
    services/

And inside `resources` can be any number of subdirectories and files. Like
this::

    $ tree -F resources/
    resources/
    |-- ssh_keys/
    |   |-- deploy1
    |   |-- deploy1.pub
    |   `-- old_keys/
    |       |-- deploy_key
    |       `-- deploy_key.pub
    `-- other/
        `-- script.sh

So now, in ~git files within your `root` in a service, you can reference these
keys by relative path.

Like this::

    $ cat services/example/0.0.1/root/test~git
    http://example.com/repo.git master ssh_keys/deploy1

The ~git extension knows to look in the `resources` directory for the file
`ssh_keys/deploy1`, which is the secret key needed to deploy that git
repository.

You can also use resources with :ref:`actionreaction`. Just specify the command
like this::

    {
        "run" : {
            "commands" : ["resources/test.sh"]
        },
        "go for it" : {
            "commands" : ["resources/other/file arg1 arg2", "resources/this.py", "touch /tmp/out"]
        }
    } 

This defines two actions. The first, `run`, uses one resource called test.sh.
The file resources/test.sh will be extracted to a temporary location, made
executable, and then executed with no arguments.

The second action `go for it` defines three commands to run in order. The first
two are resources. The first resource will have two command line arguments
passed to it.

.. _tests:

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


.. _global-configuration:

Global Configuration
-----

Squadron keeps the global config in the default location /home/user/.squadron
If you are root the default in /etc/squadron

It also looks for config in the following places:
 - /etc/squadron/config
 - /usr/local/etc/squadron/config
 - ~/.squadron/config

Let's go over some of the configuration values and sections:

Daemon
^^^^^^
    - polltime - frequency in seconds that we check the git repo for changes

Squadron
^^^^^^^^
    - keydir - where we store any ssh keys
    - nodename - name you want for the node, used to determine which node
      config applies to this machine
    - statedir - directory to keep previous state of squadron
    - send_status - whether or not to send node status to remote server defined
      in [status] section

Status
^^^^^^
    - status_host where to send status to
    - status_apikey - key used for identity
    - status_secret - shared secret to verify identity

Log
^^^
    This section is a bit special, you can enter as many lines as you want here
    so long as they follow the following format defined in the example:
    
    debugonly = DEBUG file /tmp/log

    - debugonly - just a friendly name, not used for anything MUST BE UNIQUE.
    - DEBUG - Level to log must match one of `Python's log levels <http://docs.python.org/2/library/logging.html#logging-levels>`_
    - file - type of log, in this case this is a simple file log
    - /tmp/log - parameter(s) for the type of log, in this case the file to log
    to

    We support three types of logs at the moment
        file:
            - expects file to log to as parameter
        stream:
            - expects stdout or stderr as the parameter
        rotatingfile:
            - file to log to
            - max file size in bytes
            - max number of files to backup 
    
    Example of rotating file:
    rotate = DEBUG rotatingfile /tmp/rot 500 2


