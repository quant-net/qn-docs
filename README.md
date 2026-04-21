Build Instructions
==================

1. Ensure you have the following packages installed and available in your Python path:
   * quantnet_controller
   * quantnet_agent
   * quantnet_mq

```
pip install "sphinx<9" sphinx-rtd-theme sphinx-click readthedocs-sphinx-search sphinxcontrib.bibtex sphinx-toolbox pyyaml
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


Versioned Builds
================

The documentation supports multiple versions using a build script
(`build_docs.py`) that iterates over entries in `versions.yaml` and the
`main` branch. A version selector flyout panel appears at the bottom of
the sidebar, matching the Read the Docs style.

### Single-version build (development)

For day-to-day development, the standard single-version build works as usual:

```
make html
```

### Building all versions locally

```
python build_docs.py --output-dir ./pages
```

This builds `latest` from `main` and each version listed in `versions.yaml`
into subdirectories under `./pages/` (e.g., `./pages/latest/`, `./pages/1.0/`).

### Adding a new version

When a new `quantnet_controller` release is made:

1. Ensure the `qn-docs` content is updated for the release.
2. Tag the commit: `git tag v<MAJOR>.<MINOR>.<PATCH>`
3. Push the tag: `git push origin v<MAJOR>.<MINOR>.<PATCH>`
4. Add the version to `versions.yaml`:
   ```yaml
   "<MAJOR>.<MINOR>":
     tag: "v<MAJOR>.<MINOR>.<PATCH>"
   ```
5. Commit and push `versions.yaml` to `main`.
6. The CI workflow will automatically build and deploy all versions.


Publishing the docs
===================

Documentation is deployed to GitHub Pages via the CI workflow. Pushes to
`main` and version tags (`v*`) trigger a full rebuild of all versions.
