import os
import subprocess
import warnings
from pathlib import Path

import iris


def load_cube(filename, var):
    with warnings.catch_warnings():
        # Suppress warning for invalid units
        warnings.filterwarnings(
            action="ignore",
            category=UserWarning,
        )
        cube = iris.load_cube(filename, var)
    return cube


def load_cubes(filename):
    with warnings.catch_warnings():
        # Suppress warning for invalid units
        warnings.filterwarnings(
            action="ignore",
            category=UserWarning,
        )
        cube = iris.load(filename)
    return cube


# Using https://stackoverflow.com/revisions/13197763/9
class ChangeDirectory:
    """Context manager for changing the current working directory"""

    def __init__(self, new_path):
        self.new_path = Path(new_path).expanduser()
        self.saved_path = Path.cwd()

    def __enter__(self):
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)


def run_model():
    with ChangeDirectory("../aoscm/runtime/scm-classic/PAPA"):
        print("Running model")
        subprocess.run(
            [
                "/Users/valentina/dev/aoscm/sources/util/ec-conf/ec-conf",
                "-p",
                "valentinair",
                "config-run.xml",
            ],
            capture_output=True,
        )
        subprocess.run([], executable="./ece-scm_oifs+nemo.sh", capture_output=True)
        print("Model run successful")
