import os
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr


class ChangeDirectory:
    """Context manager for changing the current working directory.

    Use as follows:
    ```python
    with ChangeDirectory(target_directory):
        # this code will be executed inside `target_directory`
        pass
    # this code will be executed in the original working directory
    ```

    Implementation copied from [Brian M. Hunt](https://stackoverflow.com/revisions/13197763/9).
    """

    def __init__(self, new_path):
        self.new_path = Path(new_path).expanduser()
        self.saved_path = Path.cwd()

    def __enter__(self):
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)


class OIFSPreprocessor:
    """Preprocessor for Output Data from the OpenIFS SCM.

    - converts the `time` coordinate to valid datetime objects, computed relative to the simulation start date, `origin`
    - optional: applies a time shift for local time zones using `time_shift`
    """

    def __init__(
        self, origin: pd.Timestamp, time_shift: pd.Timedelta = pd.Timedelta(0)
    ):
        """Constructor.

        :param origin: start date (+ time) of the simulation
        :type origin: pd.Timestamp
        :param time_shift: time shift to apply for local time, defaults to pd.Timedelta(0)
        :type time_shift: pd.Timedelta, optional
        """
        self.origin = origin
        self.time_shift = time_shift

    def preprocess(self, ds: xr.Dataset) -> xr.Dataset:
        """Preprocess function for use with `xr.open_mfdataset()`.

        :param ds: dataset as loaded from disk
        :type ds: xr.Dataset
        :return: preprocessed dataset
        :rtype: xr.Dataset
        """
        ds = ds.assign_coords(time=self.origin + ds.time.data + self.time_shift)
        return ds


class NEMOPreprocessor:
    """Preprocessor for Output Data from the NEMO SCM.

    - drops the meaningless horizontal dimension
    - renames the time coordinate to `time`
    - sets the correct start date (NEMO always starts its output at 00:00 UTC)
    - applies a time shift for local time zones
    """

    def __init__(
        self, origin: pd.Timestamp, time_shift: pd.Timedelta = pd.Timedelta(0)
    ):
        """Constructor.

        :param origin: start date (+ time) of the simulation
        :type origin: pd.Timestamp
        :param time_shift: time shift to apply for local time, defaults to pd.Timedelta(0)
        :type time_shift: pd.Timedelta, optional
        """
        self.origin = origin
        self.fix_start_date = False
        if self.origin.hour != 0:
            self.fix_start_date = True
        self.time_shift = time_shift

    def preprocess(self, ds: xr.Dataset) -> xr.Dataset:
        """Preprocess function for use with `xr.open_mfdataset()`.

        :param ds: dataset as loaded from disk
        :type ds: xr.Dataset
        :return: preprocessed dataset
        :rtype: xr.Dataset
        """
        ds = ds.isel(y=0, x=0)
        ds = ds.rename(time_counter="time")
        if self.fix_start_date:
            time_as_timedelta = ds.time.data - np.datetime64(self.origin.date())
            ds = ds.assign_coords(
                time=time_as_timedelta + self.origin + self.time_shift
            )
        else:
            ds = ds.assign_coords(time=ds.time.data + self.time_shift)
        return ds


class OIFSEnsemblePreprocessor:
    def __init__(self, time_shift: pd.Timedelta = pd.Timedelta(0)):
        self.time_shift = time_shift

    def preprocess_ensemble(self, ds: xr.Dataset) -> xr.Dataset:
        source_file = Path(ds.encoding["source"])
        coupling_scheme = source_file.parent.name
        if coupling_scheme == "schwarz":
            coupling_scheme = "converged SWR"

        start_date = pd.Timestamp(
            source_file.parent.parent.parent.name.replace("_", ", ")
        )
        initial_condition = source_file.parent.parent.name
        ds = ds.expand_dims(
            coupling_scheme=[coupling_scheme],
            start_date=[start_date + self.time_shift],
            initial_condition=[initial_condition],
        )
        return ds

class NEMOEnsemblePreprocessor:
    def __init__(self, time_shift: pd.Timedelta = pd.Timedelta(0)):
        self.time_shift = time_shift

    def preprocess_ensemble(self, ds: xr.Dataset) -> xr.Dataset:
        source_file = Path(ds.encoding["source"])
        coupling_scheme = source_file.parent.name
        if coupling_scheme == "schwarz":
            coupling_scheme = "converged SWR"

        start_date = pd.Timestamp(
            source_file.parent.parent.parent.name.replace("_", ", ")
        )
        initial_condition = source_file.parent.parent.name
        ds = ds.isel(y=0, x=0)
        ds = ds.rename(time_counter="time")
        ds = ds.assign_coords(time=ds.time.data - np.datetime64(start_date.date()))
        ds = ds.expand_dims(
            coupling_scheme=[coupling_scheme],
            start_date=[start_date + self.time_shift],
            initial_condition=[initial_condition],
        )
        return ds

class OASISPreprocessor:
    def preprocess(self, ds: xr.Dataset) -> xr.Dataset:
        ds = ds.isel(ny=0, nx=0)
        return ds