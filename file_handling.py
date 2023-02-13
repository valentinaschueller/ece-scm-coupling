import numpy as np
import xarray as xr


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
