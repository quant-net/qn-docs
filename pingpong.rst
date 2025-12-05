PingPong
********

PingPong protocol
-----------------

This tutorial provides the steps necessary to introduce a simple ping-pong protocol between the Controller and Agent. Besides being an informative exercise, this protocol may be useful in characterizing the Controller's messaging reachability and latency to one or more running Agents in your control plane network.

Our ping-pong protocol requirements are as follows:

* Allow an external client to contact the Controller using a ``pingPongRequest`` message

* The request message will contain the following information:

  * A list of destinations (Agent IDs)
  * The number of ping-pong iterations

* The client will asynchronously receive a ``pingPongRecord`` message with the results for each destination specified in the request

  * The number of successful ping-pong attempts
  * The averaged round-trip-time information

* The Controller will maintain a ``pingPongRecord`` in its database for the last request made to each Agent


With the requirements stated, you will exercise the following control plane integrations to implement this functionality:

* Define a protocol schema for the :doc:`Message Bus<comms>`
* Create a ProtocolPlugin for the Controller that handles external client requests, sends pings to the Agents, and tracks the protocol results.
* Create a CommandInterpreter for the Agent that responds to pings from the Controller.
* Create a test client to make ``pingPingRequests`` and display results.

The complete ping-pong tutorial source code may be found `here <https://github.com/quant-net/quant-net-plugins/blob/develop/plugins/pingpong>`_

Protocol schema
---------------

Three types of messages are required for our ping-pong protocol:

#. The request and response from the client to Controller

#. The ``ping`` and ``pong`` that are communicated between the Controller and Agents

#. The summary record that is communicated back to the client.

Below is the ``pingPongRequest`` definition. This protocol message is intended use is as an RPC in the control plane, so it contains the required fields ``cmd``, ``agentId``, and ``payload``.  The payload contains the request-specific fields including ``type`` (a string), ``destinations`` (an array of strings), and ``iterations`` (an integer). 

.. code-block:: yaml

        PingPongRequest:
            title: pingPongRequest
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
                      - type
                      - destinations
                      - iterations
                properties:
                    type:
                        type: string
                    destinations:
                        type: array
                        minItems: 1
                        items:
                            type: string
                    iterations:
                        type: number

The ``pingPongRecord`` will serve two purposes by defining 1) the structure of data to save for each Agent's ping request, and 2) the message format for the summary record to communicate back to the requesting client. Our record contains an ``id`` field to identify the Agent, ``phase`` to indicate start/done/failure states, start and end timestamps to time the request, and a number of statistic fields for summary reporting.
 
.. code-block:: yaml

    PingPongRecord:
      title: pingPongRecord
      type: object
      required:
        - id
        - phase
      properties:
        id:
          type: string
        phase:
          type: string
        start_ts:
          type: number
        end_ts:
          type: number
        result:
          type: string
        iterations:
          type: number
        rtt_min:
          type: number
        rtt_max:
          type: number
        rtt_avg:
          type: number
        rtt_mdev:
          type: number
        successes:
          type: number


The ``ping`` and ``pong`` messages are ommitted for brevity but may be found in the complete ping-pong YAML located within the `schema/ <https://github.com/quant-net/quant-net-plugins/blob/develop/plugins/schema/pingpong.yaml>`_ sub-directory.


Controller ProtocolPlugin
-------------------------

Now that we have a complete schema definition, we can begin to implement the protocol implementation for the Controller. Inside of ``pingpong/__init__.py`` we define an instance of the abstract ``ProtocolPlugin`` class. The ``PingPongProtocol`` will adhere to this abstract interface and allow for the registration of handlers that match any received messages (i.e. "commands") defined in our ping-pong schema. 

.. code-block:: python

    import logging
    from quantnet_controller.common.plugin import ProtocolPlugin, PluginType
    from quantnet_controller.common.request import RequestManager, RequestType
    from quantnet_mq import Code
    from quantnet_mq.schema.models import pingpong, Status as responseStatus
    from pingponger import PingPonger

    logger = logging.getLogger(__name__)


    class PingPongProtocol(ProtocolPlugin):
        def __init__(self, context):
            super().__init__("pingpong", PluginType.PROTOCOL, context)
            self._client_commands = [
                ("pingpong.ping", None, "quantnet_mq.schema.models.pingpong.ping"),
            ]
            self._server_commands = [
                ("pingpong", self.handle_pingpong, "quantnet_mq.schema.models.pingpong.pingPongRequest"),
            ]
            self._msg_commands = list()
            self.ctx = context

            # Initialize RequestManager for protocol-type requests
            self.request_manager = RequestManager(
                context, plugin_schema=pingpong.pingPongRequest, request_type=RequestType.PROTOCOL
            )

            self._pingponger = PingPonger(config=context.config, rpcclient=context.rpcclient, msgclient=context.msgclient)

        async def handle_pingpong(self, request):
            """Handle pingpong request."""
            logger.info(f"Received pingpong request: {request.serialize()}")

            # Create plugin-specific payload object
            payload = pingpong.pingPongRequest(**request)

            rc = Code.OK

            if payload.payload.type == "ping":
                try:
                    # Create Request object with custom function
                    req = self.request_manager.new_request(payload=payload, parameters={}, func=self._pingponger.pingpong)

                    # Execute immediately without queueing
                    rc = await self.request_manager.noSchedule(req, blocking=True)

                except Exception as e:
                    logger.error(f"Could not schedule pingpong request: {e}")
                    import traceback

                    traceback.print_exc()
                    rc = Code.FAILED
            else:
                logger.error(f"Unknown pingpong request type {payload.payload.type}")
                rc = Code.FAILED

            return pingpong.pingPongResponse(
                status=responseStatus(code=rc.value, value=Code(rc).name), token=payload.payload.token
            )


The Controller plugin imports a `PingPonger <https://github.com/quant-net/quant-net-tutorials/blob/main/pingpong/pingpong/pingponger.py>`_ class that implements the ping-pong protocol logic and record management. Whenever a Controller with this plugin loaded receives a ``pingPongRequest`` it will invoke the ``handle_pingpong()`` method to begin the ping-pong protocol. The plugin also registers a ``ping`` command as a valid RPC call conforming to the specified ping-pong protocol schema.

Agent Command Interpreter
-------------------------

Our most straighforward code module for this tutorial is at the Agent side. Here we implement an instance of the abstract ``CMDInterpreter`` class to handle ping commands received from the Controller. A ``handle_ping()`` method is defined to process the ping requests. The extent of the handler processing is to construct a ``pong`` response that simply encodes a timestamp and a message that lists all of the hardware drivers loaded within the running Agent.

.. code-block:: python

    import time
    import logging
    from quantnet_mq.schema.models import pingpong, Status as responseStatus
    from quantnet_mq import Code
    from quantnet_agent.hal.HAL import CMDInterpreter

    log = logging.getLogger(__name__)

    class PingPong(CMDInterpreter):

        def __init__(self, hal):
            super().__init__(hal)

        async def handle_ping(self, request):
            log.info("Received ping request: %s", request.serialize())
            device_configured = (
                f"This agent is configured with the following drivers: {' '.join([i for i in self.hal.devs])}"
            )
            return pingpong.pong(timestamp=time.time(),
                                 message=device_configured)

        def get_commands(self):
            commands = {"pingpong.ping": [self.handle_ping,
                        "quantnet_mq.schema.models.pingpong.ping"]}
            return commands


Client program
--------------

Finally, we are able to implement a testing client to drive our new ping-pong protocol implementation.

.. code-block:: python

    import os
    import sys
    import json
    import asyncio
    from quantnet_mq.rpcclient import RPCClient
    from quantnet_mq.msgserver import MsgServer
    from quantnet_mq.schema.models import Schema

    class MyPingPonger():
        def __init__(self, destinations=list(), iters=5):
            self._dests = destinations
            self._iters = iters
            self._pending = len(self._dests)

        async def start_pingpong(self, client):
            msg = {"type": "ping", "destinations": self._dests, "iterations": self._iters}
            ret = await client.call("pingpong", msg, timeout=20.0)
            ret = json.loads(ret)
            return ret

        def handle_pong(self, msg):
            from quantnet_mq.schema.models import pingpong
            res = pingpong.pingPongRecord(**json.loads(msg))
            print(f"--- {res.id} ping statistics ---")
            print(f"{res.iterations} requests made, {res.successes} received, time {(res.end_ts-res.start_ts)*1e3:.0f}ms")
            if res.successes:
                rtt_min = float(res.rtt_min)
                rtt_avg = float(res.rtt_avg)
                rtt_max = float(res.rtt_max)
                rtt_mdev = float(res.rtt_mdev)
                print(f"rtt min/avg/max/mdev {rtt_min:.3f}/{rtt_avg:.3f}/{rtt_max:.3f}/{rtt_mdev:.3f} ms")
            self._pending -= 1

        async def main(self):
            # Setup RPC client with our PingPong schema
            Schema.load_schema("../schema/pingpong.yaml", ns="pingpong")
            client = RPCClient("pingpong-client", host=os.getenv("HOST", "localhost"))
            client.set_handler("pingpong", None, "quantnet_mq.schema.models.pingpong.pingPongRequest")
            await client.start()

            # Subscibe to pong topic
            mclient = MsgServer(host=os.getenv("HOST", "localhost"))
            mclient.subscribe("pong", self.handle_pong)
            await mclient.start()

            # Begin pingpong request
            res = await self.start_pingpong(client)

            # Wait for pong responses (as received at controller)
            while (self._pending):
                await asyncio.sleep(1)

    if __name__ == "__main__":
        dests = ["agent1", "agent2"]
        asyncio.run(MyPingPonger(dests, iters=5).main())


Our ``test_pingpong.py`` is an asyncio application that makes use of the :doc:`Message Bus<comms>` RPC and Messaging facilities to invoke the ping-pong protocol at the Controller and handle the ``pingPongRecords`` returned, respectively. Note that the test program must load the ping-pong schema file so that it can make use of the generated schema models.

Using the :doc:`Quick Start<quick>` environment, an example execution of the client with ``agent1`` and ``agent2`` specified as destinations where ``agent1`` is online but not ``agent2``:

.. code-block:: bash
    
    $ docker exec -ti controller bash
    root@e038e8ec4071:/# cd /quant-net-plugins/plugins/pingpong/

    root@e038e8ec4071:/quant-net-plugins/plugins/pingpong# HOST=broker python3 test_pingpong.py
    --- LBNL-Q ping statistics ---
    5 requests made, 5 received, time 5107ms
    rtt min/avg/max/mdev 2.704/19.802/44.927/22.162 ms
    message: Agent LBNL-Q is configured with the following drivers: exp_framework, lightsource, epc, polarimeter, egp, messaging
    --- UCB-Q ping statistics ---
    5 requests made, 5 received, time 5109ms
    rtt min/avg/max/mdev 1.964/19.341/44.573/22.769 ms
    message: Agent UCB-Q is configured with the following drivers: exp_framework, lightsource, epc, polarimeter, egp, messaging
    --- agent2 ping statistics ---
    5 requests made, 0 received, time 10009ms
