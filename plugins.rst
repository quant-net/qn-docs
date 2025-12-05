Controller Plugins
==================

Controller plugins extend the built-in functionality of the Quant-Net
control plane. Currently, there are four types of plugins, each
representing common classes of functions involved in quantum networking
experiments.

Each plugin defines both client and server commands for RPC calls, along
with the corresponding handlers that the controller must process.
Additionally, plugins can define message commands to handle non-RPC
messages. When the controller starts, it loads and initializes these
plugins, registering the provided commands in its RPC server and client
and message server.

The ``ControllerContextManager`` provides the running context of the
controller to a plugin. The ``context`` object includes the current
controller configuration, the RPC server/client, and the Message
server/client.

An example of how to use a plugin to implement message handling can be
found in the :doc:`Tutorial </tutorial>`.



Abstract Interfaces
--------------------------


.. automodule:: quantnet_controller.common.plugin
    :members:
    :member-order: bysource
    :exclude-members: PluginType



Request Manager
--------------------------


.. automodule:: quantnet_controller.common.request
    :members:
    :member-order: bysource
    :exclude-members: