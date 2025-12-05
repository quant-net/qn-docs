============================
Protocol Modules
============================

Protocols in the Quant-Net control plane are a type of :doc:`Plugin
</plugins>` that provides the :doc:`Controller </server>` the ability to
handle requests from a client. A protocol defines a list of commands and
their corresponding handlers, which are registered as callbacks to
manage each command.

When a message is received in the controller via the :doc:`Message Bus
<comms>`, the corresponding registered handler is invoked to process the
message. Since protocols often involve interaction between the
:doc:`Controller </server>` and :doc:`Agents </agent>`, they are
provided access to a `ControllerContextManager` object. This object
contains controller configurations and instances of the RPC
server/client.

The abstract class for a protocol is defined in :doc:`Plugin
</plugins>`, and an example of how to use a protocol to implement
message handling can be found in the :doc:`Tutorial </tutorial>`. This
example demonstrates how a plugin can extend the built-in control plane
functionality, along with :doc:`Agent Command Interpreters
</interpreters>`.
