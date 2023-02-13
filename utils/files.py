import os
from pathlib import Path

import jinja2
import numpy as np
import xarray as xr


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


class OIFSPreprocessor:
    """Preprocessor for Output Data from the OpenIFS SCM."""

    def __init__(
        self, origin: np.datetime64, time_shift: np.timedelta64 = np.timedelta64(0)
    ):
        self.origin = origin
        self.time_shift = time_shift

    def preprocess(self, ds: xr.Dataset) -> xr.Dataset:
        fixed_ds = ds.assign_coords(
            {"time": self.origin + ds.time.data + self.time_shift}
        )
        return fixed_ds


class NEMOPreprocessor:
    """Preprocessor for Output Data from the NEMO SCM."""

    def __init__(self, time_shift: np.timedelta64 = np.timedelta64(0)):
        self.time_shift = time_shift

    def preprocess(self, ds: xr.Dataset) -> xr.Dataset:
        fixed_ds = ds.assign_coords(
            {"time_counter": ds.time_counter.data + self.time_shift}
        )
        return fixed_ds
