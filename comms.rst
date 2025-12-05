QUANT-NET Message Bus
#####################

.. image:: https://img.shields.io/pypi/v/quantnet_mq.svg
        :target: https://pypi.python.org/pypi/quantnet_mq


.. github-shield::
    :last-commit:
    :repository: qn-mq
    :branch: main

The QUANT-NET Message Bus module provide RPC and Publish/Subscribe capabilities for the control plane, and the package is a common dependency for the :doc:`Controller </server>` and :doc:`Agent </agent>` components. The ``quantnet_mq`` module provides the following functionalies:

* Remote procedure call (RPC) client and server implementations
* Publish/Subscribe (pub/sub) client and server implementations
* Core schemas for the QUANT-NET Control Plane network data model
* Auto-generated Python objects for all defined schema

Example Usage
*************

* RPC client

.. code-block:: python

    import asyncio
    from quantnet_mq.rpcclient import RPCClient

    async def main():
        client = RPCClient("example_client")
        client.set_handler("myRequest", None,
            "quantnet_mq.schema.models.myns.myRequest")
        await client.start()

        # send a message and wait up to for a response 5s
        msg = {"arg1": "value1", "arg2": 999.99}
        req = await client.call("myRequest, msg, timeout=5.0)
        print (req)

    if __name__ == "__main__":
        asyncio.run(main())

* Pub/Sub receiver

.. code-block:: python

    import asyncio
    from quantnet_mq.rpcclient import MsgServer

    async def handle_msg(data):
        print (data)

    async def main():
        client = MsgServer()
        mclient.subscribe("mytopic", self.handle_msg)
        await mclient.start()
        # wait as long as needed here ...

    if __name__ == "__main__":
        asyncio.run(main())


Loading user-defined schema
***************************

With user-defined protocol plugins, it may often be necessary to dynamically load the necessary schema definitions. 

* Completing the ``myns`` RPC example above:

.. code-block:: python

    from quantnet_mq.rpcclient import RPCClient
    from quantnet_mq.schema.models import Schema

    async def main(self):
        Schema.load_schema("../schema/example.yaml", ns="myns")

        client = RPCClient("myRequest")
        client.set_handler("myRequest", None,
            "quantnet_mq.schema.models.myns.myRequest")
        await client.start()

        from quantnet_mq.schema.models import myns
        # use namespaced objects ...


There is special handling for schema definitions that reference ``objects.yaml``.  This core schema packaged with ``quantnet_mq`` provides a set of common object types, including RPC response and Status formats, that may be useful. The source `schema file <https://github.com/quant-net/quant-net-mq/blob/develop/quantnet_mq/schema/objects/objects.yaml>`_ contains further details.

For example, a user-defined schema may contain a reference of the form:

.. code-block:: yaml

    properties:
      status:
        $ref: "objects.yaml#/components/schemas/Status"


Working with auto-generated schema objects
******************************************

It is straighforward to debug and test newly defined schema using the Python REPL.

Using the following ``example.yaml`` schema:

.. code-block:: yaml

    ---
    asyncapi: "2.6.0"
    id: "urn:gov:quant-net"
    info:
      description: "Quant-Net Simple Example"
      title: "RPC Example Endpoint"
      version: "1.0.0"
    components:
      messages:
        RequestMessage:
        name: RequestMessage
        messageId: example.request
        payload:
            "$ref": "#/components/schemas/RequestMessage"
    schemas:
        RequestMessage:
          title: myRequest
          type: object
        required:
          - cmd
          - agentId
          - payload
        properties:
          cmd:
            type: string
          agentId:
            type: string
          payload:
            type: object
            required:
              - arg1
              - arg2
            properties:
              arg1:
                type: string
              arg2:
                type: number


We may then load and use the schema objects directly using ``quantnet_mq``:

.. code-block:: python

    >>> from quantnet_mq.schema.models import Schema
    >>> from quantnet_mq.schema import models
    >>> Schema.load_schema("example.yaml", ns="myns")
    >>> models.myns
    <module 'myns'>
    >>> req = models.myns.myRequest()
    >>> try:
    ...   req.payload = {"arg1": "Hello", "arg2": "World"}
    ... except Exception as e:
    ...   print (e)
    ... 
    World is neither an integer nor a float 
    while setting 'arg2' in payload_<anonymous>
    >>>
    >>> req.payload = {"arg1": "Hello", "arg2": 99.99}
    >>> req.agentId = "agent1"
    >>> req.cmd = "myRequest"
    >>> req.serialize()
    '{"cmd": "myRequest", "agentId": "agent1", "payload": {"arg1": "Hello", "arg2": 99.99}, "agentID": "agent1", "command": "myRequest"}'
    >>>
