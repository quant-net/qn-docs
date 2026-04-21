#!/usr/bin/env python3
"""Build versioned documentation for QUANT-NET Control Plane.

This script builds documentation for the latest (main) version and all
tagged versions listed in versions.yaml. Each version is built into its
own subdirectory under the output directory.

For each version, the script installs the pinned packages listed in
versions.yaml so that autodoc/code introspection matches the release.

Usage:
    python build_docs.py [--pages-root URL] [--output-dir DIR]

Environment variables set for each build:
    build_all_docs   - Signals conf.py to populate html_context
    current_version  - The version label (e.g., "latest", "1.0")
    pages_root       - The base URL for the deployed documentation

Based on: https://www.codingwiththomas.com/blog/my-sphinx-best-practice-for-a-multiversion-documentation-in-different-languages
"""

import argparse
import os
import shutil
import subprocess
import sys

import yaml


def install_packages(packages):
    """Install the given list of pip packages.

    Args:
        packages: List of pip package specifiers (e.g., ["quantnet-server==1.0.0"]).
                  If None or empty, installs the latest versions of the
                  default packages.
    """
    if packages:
        print(f"  Installing pinned packages: {packages}")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--force-reinstall"]
            + packages,
            check=True,
        )
    else:
        # No pinned packages — install latest
        default_packages = ["quantnet-server", "quantnet-agent", "quantnet-mq"]
        print(f"  Installing latest packages: {default_packages}")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--force-reinstall"]
            + default_packages,
            check=True,
        )


def build_doc(version, tag, packages=None):
    """Build documentation for a specific version/tag.

    Args:
        version: Version label (e.g., "latest", "1.0.0").
        tag: Git tag or "main" for the latest branch.
        packages: Optional list of pip package specifiers to install.
    """
    os.environ["current_version"] = version
    print(f"\n{'='*60}")
    print(f"Building version: {version} (tag: {tag})")
    print(f"{'='*60}\n")

    if tag != "main":
        subprocess.run(["git", "checkout", tag], check=True)
        # Always use the latest conf.py, templates, and versions.yaml
        subprocess.run(["git", "checkout", "main", "--", "conf.py"], check=True)
        subprocess.run(["git", "checkout", "main", "--", "versions.yaml"], check=True)
        subprocess.run(
            ["git", "checkout", "main", "--", "_templates/"], check=True
        )

    # Install the correct packages for this version
    install_packages(packages)

    subprocess.run(["make", "html"], check=True)


def move_dir(src, dst):
    """Move build output to the target directory."""
    os.makedirs(dst, exist_ok=True)
    # Copy contents of src into dst
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)


def create_redirect(output_dir):
    """Create a root index.html that redirects to /latest/."""
    redirect_html = """\
<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="refresh" content="0; url=latest/">
    <title>Redirecting to latest docs</title>
  </head>
  <body>
    <p>Redirecting to <a href="latest/">latest documentation</a>...</p>
  </body>
</html>
"""
    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write(redirect_html)

    # Prevent GitHub Pages Jekyll processing
    open(os.path.join(output_dir, ".nojekyll"), "w").close()


def main():
    parser = argparse.ArgumentParser(description="Build versioned QNCP docs")
    parser.add_argument(
        "--pages-root",
        default="",
        help="Base URL for the deployed docs (e.g., /qn-docs)",
    )
    parser.add_argument(
        "--output-dir",
        default="../pages",
        help="Output directory for all built versions (default: ../pages)",
    )
    args = parser.parse_args()

    # Abort if tracked files have uncommitted changes, since the build
    # process checks out different tags and restores from main, which
    # would overwrite any local modifications.
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        capture_output=True, text=True,
    )
    if result.stdout.strip():
        print("ERROR: Uncommitted changes detected in tracked files.")
        print("Please commit or stash your changes before running this script.")
        print("Dirty files:")
        print(result.stdout)
        sys.exit(1)

    os.environ["build_all_docs"] = "True"
    os.environ["pages_root"] = args.pages_root

    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Load version manifest
    with open("versions.yaml", "r") as yaml_file:
        docs = yaml.safe_load(yaml_file)

    # Build "latest" from main branch (uses latest packages)
    build_doc("latest", "main", packages=None)
    move_dir("./_build/html/", os.path.join(output_dir, "latest/"))
    subprocess.run(["make", "clean"], check=True)

    # Build each tagged version with its pinned packages
    if docs:
        for version, details in docs.items():
            tag = details.get("tag", version)
            packages = details.get("packages")
            build_doc(str(version), tag, packages=packages)
            move_dir(
                "./_build/html/",
                os.path.join(output_dir, str(version) + "/"),
            )
            subprocess.run(["make", "clean"], check=True)
            # Restore main branch for next iteration
            subprocess.run(["git", "checkout", "main", "--", "."], check=True)

    # Create root redirect
    create_redirect(output_dir)

    print(f"\n{'='*60}")
    print(f"All versions built successfully in: {output_dir}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
