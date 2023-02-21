import os
from pathlib import Path

import pandas as pd
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
        self, origin: pd.Timestamp, time_shift: pd.Timedelta = pd.Timedelta(0)
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

    def __init__(self, time_shift: pd.Timedelta = pd.Timedelta(0)):
        self.time_shift = time_shift

    def preprocess(self, ds: xr.Dataset) -> xr.Dataset:
        fixed_ds = ds.assign_coords(
            {"time_counter": ds.time_counter.data + self.time_shift}
        )
        return fixed_ds

class OIFSEnsemblePreprocessor:
    def __init__(self, time_shift: pd.Timedelta = pd.Timedelta(0)):
        self.time_shift = time_shift
    
    def preprocess_ensemble(self, ds: xr.Dataset) -> xr.Dataset:
        source_file = Path(ds.encoding["source"])
        coupling_scheme = source_file.parent.name
        if "schwarz" in coupling_scheme:
            coupling_scheme = "converged SWR"
        
        start_date = pd.Timestamp(source_file.parent.parent.parent.name.replace("_", ", "))
        initial_condition = source_file.parent.parent.name
        ds = ds.assign_coords(time=start_date + ds.time.data + self.time_shift)
        ds = ds.expand_dims(
            coupling_scheme=[coupling_scheme],
            start_date=[start_date],
            initial_condition=[initial_condition],
        )
        # reorder coordinates to prevent monotonicity issue: https://github.com/pydata/xarray/issues/6355
        ds = ds[["time", "start_date", "coupling_scheme", "initial_condition", "nlev", "nlevp1", "nlevs", *list(ds.data_vars)]]
        return ds
    
    def preprocess_schwarz_iterations(self, ds: xr.Dataset) -> xr.Dataset:
        source_file = Path(ds.encoding["source"])
        _, iteration = source_file.parent.name.split("_")
        
        start_date = pd.Timestamp(source_file.parent.parent.parent.name.replace("_", ", "))
        initial_condition = source_file.parent.parent.name
        ds = ds.assign_coords(time=start_date + ds.time.data + self.time_shift)
        ds = ds.expand_dims(
            start_date=[start_date],
            initial_condition=[initial_condition],
            schwarz_iteration=[int(iteration)],
        )
        # reorder coordinates to prevent monotonicity issue: https://github.com/pydata/xarray/issues/6355
        ds = ds[["time", "start_date", "schwarz_iteration", "initial_condition", "nlev", "nlevp1", "nlevs", *list(ds.data_vars)]]
        return ds