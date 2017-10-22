|Build Status|

configlib
=========

A bit desesperate by the lack of good and easy to use configuration
libraries in python, I decided to write this one. The two main goals
are: - Make it easy for the you to describe the data you use to
configurate your project and be able to save and load it in one line -
Make it easy for the user of your code to modify his configuration
through the command line

Installation
~~~~~~~~~~~~

Install via pip comming soon !

User interface
--------------

The end user can easily see his configuration with

::

    python config.py --show

That will print in colors (if availaible) his config:

.. figure:: assets/show%20config.PNG
   :alt: See your configuration in colors

   See your configuration in colors

He is able to see what are all the fields easily with

::

    python config.py --list

.. figure:: assets/help.PNG
   :alt: --help

   --help

He can change each field in an interactive prompt, for the whole
configuration or only a sub configuration by one of the following. He
can also directly set one field via the command line:

::

    python config.py
    python config.py colors.castle
    python config.py age=42
    python config.py colors.walls.east=#ffaa77

Developper interface
--------------------

Simple configuration
~~~~~~~~~~~~~~~~~~~~

Fields
^^^^^^

*Documentation needs to be done*

Hints
^^^^^

*Documentation needs to be done*

Types
^^^^^

*Documentation needs to be done*

More advanced configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Documentation needs to be done*

Install
~~~~~~~

There are a few requirements that you can download with pip:

::

    pip install click pygments

For windows users, you will need pyreadline because readline isn't in
the stdlib.

::

    pip install pyreadline

.. |Build Status| image:: https://travis-ci.org/ddorn/configlib.svg?branch=v1.1.12
   :target: https://travis-ci.org/ddorn/configlib
