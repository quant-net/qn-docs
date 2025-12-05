============================
Monitoring Module
============================

Monitoring Plugin
-----------------

The :doc:`Controller </server>` provides quantum network monitoring
capabilities through a monitoring plugin interface, which defines
handlers for monitoring messages. A monitoring plugin must implement the
abstract method ``handle_resource_update()`` to manage monitoring events
received from a ``msgserver`` that listens to a chosen topic.

The built-in monitoring plugin can be used to handle monitoring events
received by the controller. It listens to the ``monitoring`` topic for
messages of type ``NodeState``. Upon receiving a message, the plugin:

1. Validates the message format based on the ``monitoring.yaml`` schema
   defined in ``quantnet_mq/schema/messages``
2. Stores the event object in the built-in database

Protocol
--------

The :doc:`QuantNet MQ </comms>` defines a built-in monitoring message
format in JSON, which includes the following fields:

- rid: ``str`` - Resource ID
- ts: ``str`` - UTC timestamp
- eventType: ``enum<str>`` - Type of event
- value: ``str/int/float`` - Value of the monitored resource

QN agents and other resources connected to the message broker can send
monitoring messages to the ``monitoring`` topic. These messages will be
processed by the monitoring plugin in the controller.
