Quick Start Instructions
========================

Prerequisites
-------------

Before you begin, ensure the following:

* Docker and Docker Compose are installed on your system.
* Access to ghcr.io registry.


Docker Environment
------------------------------------

Clone the ``qn-docker`` repository::

	git clone git@github.com:quant-net/qn-docker.git

The ``qn-docker`` repository contains the docker compose file, Dockerfile, and example configuration files for the Controller and Agent components of the QUANT-NET control plane.

* ``qn-server``: the QNCP Controller
* ``qn-agent``: the QNCP Agents

.. * ``qn-api``: the API service for user interface
.. * ``qn-sim``: the simulation framework


Starting services
-----------------

Start all ``QNCP`` services::

	docker compose up -d

It might take tens of seconds for services to stabilize. The example configuration consists of a single Controller instance and a total of 2 registering Agents representing 2 Q-nodes.

This environment is sufficient to work through the 2 tutorials provided in the documentation.


Key Features for Development
-----------------------------

* Volumes for Live Code Changes

Use bind mounts to sync local source code with the container. Changes to your local files are reflected in the container without rebuilding the image:

.. code-block:: yaml

	volumes:
            - ./conf:/opt/quantnet/etc

* Environment Variables

Set environment-specific variables in the docker-compose.yml file or in a separate .env file:

.. code-block:: yaml

	environment:
            - QUANTNET_HOME=/opt/quantnet
      

Commands for Development
------------------------

* Start Services::

	docker-compose up

* Use the --build flag to rebuild images::

	docker-compose up --build

* Stop Services::

	docker-compose down

* To remove volumes, add the --volumes flag::
	
	docker-compose down --volumes

* Execute commands in a running container::

	docker-compose exec controller bash

* View Logs::

	docker-compose logs -f controller


