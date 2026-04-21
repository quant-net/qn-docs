#!/usr/bin/env python3
"""Build versioned documentation for QUANT-NET Control Plane.

This script builds documentation for the latest (main) version and all
tagged versions listed in versions.yaml. Each version is built into its
own subdirectory under the output directory.

Usage:
    python build_docs.py [--pages-root URL]

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


def build_doc(version, tag):
    """Build documentation for a specific version/tag."""
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
        help="Base URL for the deployed docs (e.g., https://quant-net.github.io/qn-docs)",
    )
    parser.add_argument(
        "--output-dir",
        default="../pages",
        help="Output directory for all built versions (default: ../pages)",
    )
    args = parser.parse_args()

    os.environ["build_all_docs"] = "True"
    os.environ["pages_root"] = args.pages_root

    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Build "latest" from main branch
    build_doc("latest", "main")
    move_dir("./_build/html/", os.path.join(output_dir, "latest/"))
    subprocess.run(["make", "clean"], check=True)

    # Build each tagged version from versions.yaml
    with open("versions.yaml", "r") as yaml_file:
        docs = yaml.safe_load(yaml_file)

    if docs:
        for version, details in docs.items():
            tag = details.get("tag", version)
            build_doc(str(version), tag)
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
