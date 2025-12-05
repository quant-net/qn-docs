Installation
============

The ``QUANT-NET`` control plane software is distributed as both source via Github and as ``Python`` packages. These packages can be installed using the ``"pip install"`` command.

Source Code Repositories
------------------------

    |qn-server| `qn-server`
    
    |qn-agent| `qn-agent`

    |qn-mq| `qn-mq`

.. |qn-server| github-shield::
    :last-commit:
    :repository: qn-server
    :branch: main

.. |qn-agent| github-shield::
    :last-commit:
    :repository: qn-agent
    :branch: main

.. |qn-mq| github-shield::
    :last-commit:
    :repository: qn-mq
    :branch: main

Python packages via PyPI
------------------------

    |qn-server-py| `qn-server`
    
    |qn-agent-py| `qn-agent`

    |qn-mq-py| `qn-mq`

.. |qn-server-py| pypi-shield::
    :project: quantnet-server
    :version:

.. |qn-agent-py| pypi-shield::
    :project: quantnet-agent
    :version:

.. |qn-mq-py| pypi-shield::
    :project: quantnet-mq
    :version:

Follow these steps to install each quant-net package that are availabe on public Python Package Index(PyPI):

Step 1: Ensure pip is Updated

Before installing, make sure the pip is up-to-date::

	pip install --upgrade pip

Step 2: Install the Package

Run the following command to install the package, e.g.::

	pip install quantnet-mq quantnet-agent quantnet-server

Step 3: Install Specific versions (Optional)

To install a specific version, use the following syntax::

	pip install quantnet-mq==1.0.0

Step 4: Verfiy Installation

After installation, verify the package::

	pip show quantnet-mq
