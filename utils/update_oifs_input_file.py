"""
Functions to replace prognostic variables in OIFS input file from AOSCM prognostic output.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

from utils.files import OIFSPreprocessor

input_file_start_date = pd.Timestamp("2014-07-01")


def extract_final_time_step(dataset: xr.Dataset) -> xr.Dataset:
    """
    return only the final time step of a dataset
    """
    return dataset.isel(time=-1)


def find_time_index_in_file(
    ds_with_time_axis: xr.Dataset, ds_at_time_point: xr.Dataset
) -> int:
    """
    find a single time point in a Dataset with a time axis and return the array index of this point.

    using https://stackoverflow.com/a/69283110/11247528.
    """
    time_point = pd.Timestamp(ds_at_time_point.time.data[()])
    index = ds_with_time_axis.indexes["time"].get_loc(time_point)
    return index


def replace_prognostic_variables(
    oifs_input: xr.Dataset, oifs_progvar: xr.Dataset
) -> xr.Dataset:
    """
    Replaces the values of all prognostic variables in oifs_input with those in oifs_progvar.

    The input file contains forcing data in addition to initial data -> we iterate over the data_vars of
    oifs_progvar, *not* those of oifs_input.
    Pressure values are not replaced.
    """
    for data_variable in oifs_progvar.data_vars:
        if data_variable not in oifs_input:
            raise KeyError(
                f"oifs_progvar.data_vars must be a subset oifs_input but {data_variable} is not found in oifs_input."
            )
        if "pressure" in data_variable:
            # do not replace pressure values
            continue
        oifs_input[data_variable] = oifs_progvar[data_variable]
    return oifs_input


def update_oifs_input_file_from_progvar(
    oifs_input_file: Path,
    output_progvar: Path,
    progvar_time_shift: np.timedelta64 = np.timedelta64(0),
):
    output_progvar_tEnd = extract_final_time_step(output_progvar)

    oifs_preprocessor = OIFSPreprocessor(input_file_start_date, progvar_time_shift)
    preprocessed_input_ds = xr.open_mfdataset(
        oifs_input_file, preprocess=oifs_preprocessor.preprocess
    )
    time_index = find_time_index_in_file(preprocessed_input_ds, output_progvar_tEnd)
    preprocessed_input_ds.close()

    raw_input_ds = xr.open_dataset(oifs_input_file)
    raw_input_ds[dict(time=time_index)] = replace_prognostic_variables(
        raw_input_ds.isel(time=time_index), output_progvar_tEnd
    )

    tmp_path = (
        oifs_input_file.parent / f"{oifs_input_file.stem}_tmp{oifs_input_file.suffix}"
    )
    raw_input_ds.to_netcdf(tmp_path)
    tmp_path.rename(oifs_input_file)
