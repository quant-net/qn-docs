QUANT-NET Control Plane Simulation
###################################


The QUANT-NET Simulation provides a framework for running simulations that integrate directly with the control plane. It can also be imported as a library into user applications to access utility functions.

.. .. click:: quantnet_sim.cli:main
..    :prog: quantnet_sim
..    :nested: full


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

  [mq]
  rpc_server_topic=rpc/+
  host=127.0.0.1
  port=1883

  [simulation]
  database_file_path=/opt/quantnet/etc/quant-sim-db.json
  mapping_file=mapping.yaml


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

[mq]
====

.. confval:: host
    
   :type: string

   The message queue broker host.

.. confval:: port

   :type: string

   The message queue broker port.

[simulation]
=======================

.. confval:: database_file_path

   :type: string

   The path to a writable file for internal file-based database.
   
.. confval:: mapping_file

   :type: string

   The path to a writable file that contains mapping relationships
   between topology types and python classes.
   
.. confval:: contrib_path

   :type: string

   The path to a directory that contains user defined objects.

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


Library Interfaces
------------------

.. autoclass:: quantnet_sim.simulations.client.Client

Example: ::

  from quantnet_sim import Client as QsimClient
  
  network = QsimClient().get_network()
  qnode = network.nodes['alice.lbl.gov']
  mnode = network.nodes['bob.lbl.gov']
