#!/usr/bin/env python
import os
import subprocess
from pathlib import Path

PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)

if __name__ == "__main__":
    if "{{ cookiecutter.git }}" == "y":
        _ = subprocess.check_call(["git", "init"], cwd=PROJECT_DIRECTORY)
        _ = subprocess.check_call(
            ["git", "checkout", "-b", "main"], cwd=PROJECT_DIRECTORY
        )
    else:
        Path(".gitignore").unlink()
        Path(".pre-commit-config.yaml").unlink()

    if "{{ cookiecutter.dockerfile }}" != "y":
        Path("Dockerfile").unlink()
        Path(".dockerignore").unlink()
