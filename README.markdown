ALEXANDRIA
==========

The start of a coroutine based Python messaging engine; experiments in writing a python DSL for interactive text based menu systems.

INSTALLATION
------------

You'll need to install this stuff

* generator_tools (w/ pip or easy_install)
* django (for the current database backend)
* twisted (for the USSD and XMPP runners)
* wokkel (an XMPP lib on top of Twisted)

Currently both `django` and `wokkel` are available in the `./lib/` directory. Add the directory to your `$PYTHONPATH` to be able to load to modules.

RUNNING THE CODE
----------------

There are currently 3 options for running the menus, USSD, XMPP and a command line runner. 

On OS X `twistd`, the Twisted application runner, sometimes complains about not being able write to a `dropin.cache` folder. Running `twistd` with `sudo` will fix that for you. Also, when using python2.6 or later the current Twisted version will raise warnings about the `md5` and `sha` modules being deprecated, those are ugly but not harmful.

Alexandria has two plugins for Twisted, ussd and xmpp. Running `twistd` in the root folder should list those under the available commands. Each plugin has several options running `twistd [ussd|xmpp] --help` will print those for you.

**Running a menu over USSD**

Running `twistd ussd --menu=examples.devquiz` will start the menu in `examples/devquiz.py`. You will be prompted for any other options that weren't specified on the command line but which are required. These are mostly options for connecting to the USSD gateway with, currently TruTeq.

    $ twistd --pidfile=tmp/twistd.ussd.pid ussd --menu=examples.devquiz
    username: <your truteq username>
    hostname: <your truteq hostname>
    password: <your truteq password>
    port: <your truteq port number>

Stop the process with a SIGHUP - `kill -HUP \`cat tmp/twistd.ussd.pid\``

While developing add the `-n` or `--nodaemon` option to keep the application running in the foreground.

If going into production add the `--logfile=logs/twistd.ussd.log` option to redirect the logging to the given file.

**Running a menu of XMPP**

Running a menu over XMPP is similar to the USSD transport. It only differs in the options required.

    $ twistd --pidfile=tmp/twistd.xmpp.pid xmpp --menu=examples.devquiz
    username: <your gtalk / xmpp username>
    password: <your gtalk / xmpp password>
    host: <your gtalk / xmpp host, defaults to `talk google.com`>
    port: <your gtalk / xmpp port, defaults to `5222`>

The XMPP plugin currently doesn't accept a `--menu` option yet, it is hard coded into `alexandria/twisted/xmpp.py`. This will change soon.

**Running a menu on the command**

Alexandria provides a command line client for testing menu's with. It currently expects 1 single argument, an MSISDN for the connecting client as it imitates a USSD session. It, like the XMPP transport, does not yet provide a `--menu` option.

Example: `./command-line-client 27761234567`

Returning blank will end the connection and close the process.

TODO
----

In order of *importance*:

1. Write tests and documentation

2. All transports allow a `--menu` option to specify what menu to run.

3. Allow for tree like menu structures, see the example below.

4. Create a request type object that has access to the menu system and the session storage. Simplifies the current `ms, session = yield` stuff a little bit.

5. Data store needs to be more pluggable. It can currently be changed but it is ugly and requiring all of Django just for the models is a bit of an overkill, either we choose to make use of *all* of Django or write a simple little db layer for access an sqlite3 database.


PSEUDOCODE EXAMPLE
------------------

    prompt("What is your favorite programming language?", name="start", options={
        "python": prompt('You rock! What version?', {
            "2.3": prompt("Oooh very old"),
            "2.4": prompt("Nicer...")
        }),
        "ruby": prompt("Sweet, what runtime?", {
            "mzr": prompt('classic'),
            "jruby": prompt('edgy')
            # nesting deeper
            ...
                ...
                    ...
                        ... 
                            ...
                                ...
                                    ...
                                        # ability to jump to a named anchor
                                        goto("start") 
        })
    })