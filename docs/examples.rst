.. _examples:

Examples
========

Here are examples of various problems solved with Squadron.

.. _escape:

Escape hatch
------------

Do you need to do something that Squadron can't do? Squadron wasn't designed to
support every single possible action to deploy your software, so what do you do
when you need to do something Squadron doesn't support?

Use an escape hatch!

Let's say you need to decrypt a file using GPG after downloading it. Squadron
doesn't support this, so you'll need to do it yourself::

    $ cd services/escape-hatch/0.0.1/
    $ ls -F root/
    config.sq  decrypt.sh~tpl  encrypted.sh.gpg~download

The file encrypted.sh.gpg will be downloaded from the URL contained therein.
And the script decrypt.sh will be used to decrypt it. Let's look at that
script::

    #!/bin/bash
    PASSPHRASE="@passphrase"
    echo -n "$PASSPHRASE" | gpg -d --passphrase-fd 0 -o run.sh encrypted.sh.gpg
    chmod +x run.sh

Since this is a template, the variable @passphrase will be supplied by
Squadron. We have an action (in `actions.json`)to run decrypt::

    {
        "decrypt": {
            "commands": ["./decrypt.sh"],
            "chdir": "."
        }
    }

And a reaction (in `react.json`) to execute it when appropriate::

    [
        {
            "execute":["decrypt"],
            "when": {
                "files": ["encrypted.sh.gpg"],
                "not_exists": ["run.sh"]
            }
        }
    ]

If you want to see the complete repository, simply checkout the `escape-hatch`
branch from the example Squadron repository::

    git clone -b escape-hatch https://github.com/gosquadron/example-squadron-repo.git

.. _nodejs:

Node.js
-------

Got a Node.js project? Well we've set up an example Squadron repository which
does a lot of the setup you'll need to do in your Node.js project. Simply clone
the `node` branch of the example Squadron repository::

    git clone -b node https://github.com/gosquadron/example-squadron-repo.git

The best part about this example is the :ref:`actionreaction`. Here is
`actions.json`::

    {
        "install npm deps" : {
            "commands" : ["npm install"],
            "chdir" : "code"
        },
        "rebuild" : {
            "commands" : ["npm rebuild"],
            "chdir" : "code"
        },
        "start" : {
            "commands" : ["forever start index.js"],
            "chdir" : "code"
        },
        "restart" : {
            "commands" : ["forever restart index.js"],
            "chdir" : "code",
            "not_after" : ["start"]
        }
    }

Contained in `actions.json` is almost everything you'll want to do with your
Node.js project: install dependences, rebuild for different platforms, and
start or restart your service when appropriate. To go with this is
`react.json`::

    [
        {
            "execute":["rebuild"],
            "when": {
                "always": true
            }
        },
        {
            "execute":["install npm deps"],
            "when": {
                "files":["code/package.json"],
                "not_exist":["code/node_modules"]
            }
        },
        {
            "execute":["start"],
            "when": {
                "command":"forever list | grep index.js",
                "exitcode_not": 0
            }
        },
        {
            "execute":["restart"],
            "when": {
                "files":["*"]
            }
        }
    ]

This says:

1. Always run npm rebuild in the `code` directory
2. Run npm install in the `code` directory when the `packages.json` file changes,
   or `code/node_modules/` doesn't exist
3. Start our service if it's not already running
4. If our service was already running (checked via "not_after" in
   `actions.json`) then restart it if any files were changed.

One more bit is used to make our deployment fast. Using `copy.json` to copy
`code/node_modules/` from previous runs so we don't need to redownload all of
them every time::

    [
        {
            "path": "code/node_modules/"
        }
    ]

See :ref:`copy` for more information about `copy.json`.
