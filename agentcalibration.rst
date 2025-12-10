Agent Calibration
*****************

This tutorial explains how an :doc:`Agent </agent>` brings its local
hardware into a **Ready** state using calibration tasks, and how this
interacts with the node-level scheduler described in
:doc:`Scheduling </scheduling>`.

Getting an Agent into Ready State
=================================

When an agent starts, it can calibrate attached physical devices
(sources, detectors, control electronics, etc.) before it can safely
serve user requests. QuantNet models this as a set of **local
calibration tasks** managed by the agent’s node-level scheduler.

At a high level:

* Each calibration task describes how to bring one aspect of the hardware
  into specification (e.g., laser frequency, attenuation).
* Tasks can depend on one another, and are tracked in a Directed Acyclic
  Graph (DAG), similar to the dependency handling described in
  :doc:`scheduling`.
* The agent remains **Not Ready** until all required calibration tasks
  have reached an in-spec state.

Agent States
------------

An agent can be in one of the following states:

* **Not Ready** – The agent has not finished calibrating its devices.
  One or more calibration tasks are either pending, running, or out of
  specification.
* **Ready** – All required calibration tasks are in specification and
  the agent is ready to participate in network operations and user
  requests.

An agent transitions from **Not Ready** to **Ready** only after all
required calibration tasks have completed successfully and are within
their configured validity intervals. If any task later becomes
out-of-spec (for example, due to periodicity timeout or a failed check),
the agent may leave the **Ready** state until recalibration succeeds.

Calibration Workflow
====================

During initialization, the agent:

1. Reads calibration task definitions from the configuration file.
2. Adds each task to the local task manager and constructs a dependency
   DAG to track ordering constraints.
3. Schedules calibration tasks on the node-level TDMA scheduler.
4. Monitors task status and updates both the DAG and the agent state
   (Not Ready / Ready).

Calibration is typically repeated periodically to ensure the hardware
remains within specification over time.

Local Calibration Tasks
-----------------------

A **local calibration task** is an operation that an agent executes
entirely locally to calibrate its attached devices. The task:

* Runs on the node-level scheduler, without requiring controller
  interaction for each execution.
* Can depend on the results of other local calibration tasks.
* Produces **derived parameters** that are consumed by other tasks or by
  real-time experimental functions.

Examples include:

* Tuning laser frequency to a specific atomic transition.
* Adjusting attenuation to reach a target saturation power.
* Aligning optical modes or polarizations.

Task Definition Structure
-------------------------

Calibration tasks are described in JSON, which the agent loads at
startup. Each definition typically contains:

* An identifier and human-readable name.
* Purpose and description.
* Derived parameters and validity period.
* Dependencies on other tasks.
* Details for lightweight and full-scale calibration procedures.

Below are two representative examples.

Frequency Calibration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: json

    {
        "id": "laser_frequency_calibration",
        "Name": "Frequency Calibration",
        "Purpose": "Find the resonance for the cycling transition S1/2→P1/2 near 397 nm, and use this to calibrate both state readout and doppler cooling frequencies.",
        "Derived_parameters": [
            "397_cooling_freq",
            "397_readout_frequency"
        ],
        "Periodicity": 3600,
        "Dependency": null,
        "Status_check": null,
        "Lightweight_calibration": null,
        "Full_scale_calibration": {
            "Function": "experiments/Calibrations/cal_doppler_cooling.py",
            "Class": "CalDopplerCoolingFreq",
            "Scanning_parameters": "397_AOM_Frequency",
            "Result_parameters": [
                "current_scan.plots.x",
                "current_scan.plots.y"
            ],
            "Experiment_parameters": {"use_db": true},
            "Maximum_duration": 10,
            "Analysis_function": null
        }
    }

Attenuation Calibration
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: json

    {
        "id": "laser_attenuation_calibration",
        "Name": "Attenuation Calibration",
        "Purpose": "Find the saturation power for the cycling transition S1/2→P1/2 near 397 nm, and use this to calibrate both the state readout and doppler cooling powers.",
        "Derived_parameters": [
            "397_cooling_attenuation", 
            "397_readout_attenuation"
        ],
        "Periodicity": 3600,
        "Dependency": ["laser_frequency_calibration"],
        "Status_check": null,
        "Lightweight_calibration": null,
        "Full_scale_calibration": {
            "Function": "experiments/Calibrations/cal_doppler_cooling_power.py",
            "Class": "CalDopplerCoolingPower",
            "Scanning_parameters": "397_AOM_Frequency",
            "Result_parameters": [
                "current_scan.plots.x", 
                "current_scan.plots.y"
            ],
            "Experiment_parameters": {"use_db": true},
            "Maximum_duration": 10,
            "Analysis_function": null
        }
    }

In this example:

* **Frequency Calibration** runs independently and provides
  ``397_cooling_freq`` and ``397_readout_frequency``.
* **Attenuation Calibration** depends on **Frequency Calibration**, so
  it can only be scheduled after the frequency task has completed
  successfully.

The ``Derived_parameters``, ``Lightweight_calibration``, and
``Full_scale_calibration`` sections are interpreted by the HAL and
submitted to the ExperimentFramework once scheduled by the node-level
scheduler (see :doc:`scheduling`).

Configuration File
------------------

Calibration tasks are loaded during agent initialization via a
configuration file. A minimal example is:

.. code-block:: ini

    [tasks]

    [[laser_frequency_calibration]]
    path = laser_frequency_calibration.json

    [[laser_attenuation_calibration]]
    path = laser_attenuation_calibration.json

Each ``[[task_id]]`` section references a JSON file with the task
definition. When the agent starts, it reads this section, instantiates
the corresponding tasks, and inserts them into the dependency DAG.

.. _agent-calibration-dag:

Calibration Dependency Handling
===============================

Some calibration tasks require the results of others. For example, the
*Attenuation Calibration* task depends on the *Frequency Calibration*
task. This is represented using a **Directed Acyclic Graph (DAG)**, in
the same spirit as the calibration scheduling described in
:doc:`scheduling`.

Directed Acyclic Graph (DAG)
----------------------------

The agent’s local task manager:

* Creates a DAG with a virtual root node.
* Inserts each calibration task as a node.
* Adds edges to represent dependencies (e.g., Frequency → Attenuation).

Tasks without dependencies connect directly to the root node. The DAG
enforces that:

* A task is scheduled only after all of its predecessors are in-spec.
* If a task becomes invalid, its dependent tasks are also marked
  out-of-spec and must be recalibrated.

When all calibration tasks reachable from the root are in-spec, the
agent transitions to the **Ready** state.

Initialization and Scheduling Example
-------------------------------------

The log excerpt below illustrates how an agent initializes and schedules
calibration tasks:

.. code-block:: bash

    2025-12-02 13:01:47,829 quantnet_agent.service.agent  63525     INFO Agent started with protocol namespaces:
    ....
    2025-12-02 13:01:48,043 quantnet_agent.hal.local_task_manager 63525     INFO Generating DAG
    2025-12-02 13:01:48,043 quantnet_agent.hal.node       63525    DEBUG Registering namespace scheduler
    ....
    2025-12-02 13:01:48,045 root                          63525     INFO Adding a local task: laser_frequency_calibration
    2025-12-02 13:01:48,045 root                          63525     INFO Adding a local task: laser_attenuation_calibration
    2025-12-02 13:01:48,045 quantnet_agent.hal.node       63525     INFO Agent LBNL-Q will load the followings: 
    NAME                          TYPE                          RESOURCE
    ------------------------------------------------------------
    exp_framework                 driver                        DummyExpFramework
    lightsource                   driver                        DummyLightSrc
    epc                           driver                        DummyEPC
    polarimeter                   driver                        DummyPolarimeter
    egp                           driver                        SimEGPDriver
    messaging                     driver                        PassthroughDriver
    scheduler                     build-in interpreters         scheduler.py
    calibration                   build-in interpreters         calibration.py
    experiment                    build-in interpreters         exp_framework.py
    laser_frequency_calibration     task                        qn-agent/config/
    laser_attenuation_calibration   task                        qn-agent/config/

    2025-12-02 13:01:48,091 quantnet_agent.hal.local_task_manager 63525     INFO Adding dependency in DAG
    2025-12-02 13:01:48,091 quantnet_agent.hal.local_task_manager 63525    DEBUG Adding dependency from 0 to Frequency Calibration
    2025-12-02 13:01:48,091 quantnet_agent.hal.local_task_manager 63525    DEBUG Adding dependency from Frequency Calibration to Attenuation Calibration
    2025-12-02 13:01:48,094 quantnet_agent.scheduler.scheduler 63525    DEBUG Running Frequency Calibration immediately
    ....
    2025-12-02 13:01:48,098 quantnet_agent.scheduler.scheduler 63525    DEBUG Adding a job Frequency Calibration (trigger: date[2025-12-02 19:01:48 UTC], next run at: 2025-12-02 19:01:48 UTC)
    2025-12-02 13:01:48,104 quantnet_agent.scheduler.scheduler 63525    DEBUG Running Attenuation Calibration immediately
    2025-12-02 13:01:48,107 quantnet_agent.scheduler.scheduler 63525    DEBUG Adding a job Attenuation Calibration (trigger: date[2025-12-02 19:01:58 UTC], next run at: 2025-12-02 19:01:58 UTC)

This shows:

1. The agent starts and the local task manager generates the DAG.
2. Calibration tasks are registered and loaded from configuration.
3. Dependencies are added (Frequency → Attenuation).
4. The node-level scheduler immediately runs the first-priority task
   and schedules both tasks for future runs, respecting their
   dependencies and periodicity.

In combination with the global and node-level schedulers described in
:doc:`scheduling`, this mechanism ensures that each node maintains
well-calibrated devices while still meeting real-time constraints for
user traffic.
