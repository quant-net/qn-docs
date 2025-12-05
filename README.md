Build Instructions
==================

1. Ensure you have the following packages installed and available in your Python path:
   * quantnet_controller
   * quantnet_agent
   * quantnet_mq

```
pip install sphinx-rtd-theme sphinx-click readthedocs-sphinx-search sphinxcontrib.bibtex sphinx-toolbox
```

2. Clone the docs repository

```
git clone git@github.com:quant-net/qn-docs.git
```

3. Make the HTML documents

```
cd qn-docs
make html
```

4. Use a browser to view `_build/html/index.html`


Publishing the docs
===================

TODO
