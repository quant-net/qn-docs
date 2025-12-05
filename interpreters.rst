Agent Command Interpreters
==========================

Command interpreters implement the control logic for QN functions
managed by an :doc:`Agent </agent>`. Each interpreter registers its
callback function for a specific RPC command. 

When a :doc:`Controller </server>` makes a QN function call by invoking
the corresponding RPC on an agent, the callback handles the function
execution. Each interpreter is initialized with :doc:`HAL </hal>`
instances that provide real-time device driver access, allowing the
interpreter to control real-time hardware.


Abstract Interfaces
--------------------------

Interpreter Base

.. autoclass:: quantnet_agent.hal.HAL.Interpreter


Core Interpreter

.. autoclass:: quantnet_agent.hal.HAL.CoreInterpreter
    :members:

Command Interpreter

.. autoclass:: quantnet_agent.hal.HAL.CMDInterpreter
    :members:

Scheduleable Interpreter

.. autoclass:: quantnet_agent.hal.HAL.ScheduleableInterpreter
    :members:

Local Task Interpreter

.. autoclass:: quantnet_agent.hal.HAL.LocalTaskInterpreter
    :members: