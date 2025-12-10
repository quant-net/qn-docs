QUANT-NET Controller
####################


.. pypi-shield::
    :project: quantnet-server
    :version:


.. github-shield::
    :last-commit:
    :repository: qn-server
    :branch: main

The QUANT-NET Controller provides the centralized controller functions for the control plane.

.. click:: quantnet_controller.cli:main
   :prog: quantnet_controller
   :nested: full

Configuration File
------------------

The controller makes use of an INI configuration file. The search path for the controller configuration file includes:

 * ``$QUANTNET_HOME/etc/quantnet.cfg``
 * ``/opt/quantnet/etc/quantnet.cfg``
 * ``$VIRTUAL_ENV/etc/quantnet.cfg``

Example: ::

  [common]
  logdir = /var/log/quantnet
  loglevel = INFO

  [database]
  default = mongodb://localhost:27017

  [plugins]
  path=/opt/qn-plugins

  [schemas]
  path=/opt/qn-plugins/schema

  [scheduling]
  name=BatchScheduler

  [routing]
  name=PathFinder

  [monitoring]
  name=Monitor


The configuration file may contain multiple sections as documented below.

[common]
========

.. confval:: logdir

   :type: string
   :default: ``/var/log/quantnet``

   A directory to store log files.

.. confval:: loglevel

   :type: string
   :default: ``INFO``

   The log level to configure. ``INFO``, ``WARN``, ``CRITICAL``, ``ERROR``, ``DEBUG``

[database]
==========

.. confval:: default

   :type: string
   :default: ``-``

   The database URI. Example: ``mongodb://localhost:27017``

.. confval:: schema

   :type: string

   The database schema name. [postgresql specific]

[mq]
====

.. confval:: host
    
   :type: string

   The message queue broker host.

.. confval:: port

   :type: string

   The message queue broker port.

[experiment_definition]
=======================

.. confval:: def_file_path

   :type: string

   The path to an experiment definition Python source file.

[plugins]
=========

.. confval:: path

   :type: string

   The path to a directory containing loadable controller plugins.

[schemas]
=========

.. confval:: path

   :type: string

   The path to a directory containing YAML schemas conforming to the :doc:`Message Bus </comms>` spec.

[scheduling]
============

.. confval:: name

   :type: string

   The name of a Scheduling module to make active in the Controller.

[routing]
=========

.. confval:: name

   :type: string

   The name of a Routing module to make active in the Controller.

[monitoring]
============

.. confval:: name

   :type: string

   The name of a Monitoring module to make active in the Controller.

Logging File
------------
A Python logging module ``logger.conf`` may be included in the QUANT-NET configuration path.

Example: ::

    [loggers]
    keys=root,gmqtt

    [handlers]
    keys=console

    [formatters]
    keys=simple

    [logger_root]
    level=INFO
    handlers=console

    [logger_gmqtt]
    level=CRITICAL
    handlers=console
    qualname=gmqtt
    propagate=0

    [handler_console]
    class=StreamHandler
    level=DEBUG
    formatter=simple
    args=(sys.stdout,)

    [formatter_simple]
    format=%(asctime)s - %(name)s - %(levelname)s - %(message)s


Development Install
-------------------

After downloading the source tree, pull requirements and install package in edit mode::

  pip3 install -e .
  

Local Development Environment
-----------------------------

See the :doc:`Quick Start </quick>` guide.



