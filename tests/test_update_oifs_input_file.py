import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import utils.update_oifs_input_file as uoif
from utils.files import OIFSPreprocessor


def create_dummy_ds() -> xr.Dataset:
    """
    using https://docs.xarray.dev/en/stable/generated/xarray.Dataset.html
    """
    np.random.seed(0)
    temperature = 15 + 8 * np.random.randn(2, 2, 3)
    precipitation = 10 * np.random.rand(2, 2, 3)
    lon = [[-99.83, -99.32], [-99.79, -99.23]]
    lat = [[42.25, 42.21], [42.63, 42.59]]
    time = pd.date_range("2014-09-06", periods=3)
    reference_time = pd.Timestamp("2014-09-05")
    ds = xr.Dataset(
        data_vars=dict(
            temperature=(["x", "y", "time"], temperature),
            precipitation=(["x", "y", "time"], precipitation),
        ),
        coords=dict(
            lon=(["x", "y"], lon),
            lat=(["x", "y"], lat),
            time=time,
            reference_time=reference_time,
        ),
        attrs=dict(description="Weather related data."),
    )
    return ds


def test_extract_final_time_step():
    ds = create_dummy_ds()
    final_step_ds = uoif.extract_final_time_step(ds)
    assert final_step_ds.time == ds.time[-1]
    assert (final_step_ds.temperature == ds.temperature.isel(time=-1)).all()


def test_find_time_index_in_file():
    ds = create_dummy_ds()

    # make sure the test setup still works
    time_point = pd.Timestamp("2014-09-07")
    time_point_index = 1
    assert time_point == ds.time[time_point_index]

    ds_at_time_point = ds.sel(time=time_point)

    # test the function
    found_index = uoif.find_time_index_in_file(ds, ds_at_time_point)
    assert found_index == time_point_index


def test_replace_prognostic_variables():
    data_dir = Path("tests/data")
    assert data_dir.exists()

    ff = xr.open_dataset(data_dir / "forcing_file_single_time_point.nc")
    pv = xr.open_dataset(data_dir / "progvar_single_time_point.nc")

    # make sure that original datasets are different
    assert (ff.pressure_f != pv.pressure_f).any()
    assert (ff.pressure_h != pv.pressure_h).any()
    assert (ff.t != pv.t).any()
    assert "etadotdpdeta" not in pv
    assert "etadotdpdeta" in ff
    etadotdpdeta_before = ff.etadotdpdeta.copy()

    # Wrong order: data variables not found
    pytest.raises(KeyError, uoif.replace_prognostic_variables, pv, ff)

    # Correct call
    ff = uoif.replace_prognostic_variables(ff, pv)

    assert (ff.pressure_f != pv.pressure_f).any()
    assert (ff.pressure_h != pv.pressure_h).any()
    assert (ff.t == pv.t).all()
    assert (ff.etadotdpdeta == etadotdpdeta_before).all()


def test_full_update():
    data_dir = Path("tests/data")
    assert data_dir.exists()

    ff_path = data_dir / "forcing_file.nc"
    modified_ff_path = ff_path.parent / f"modified_{ff_path.name}"
    shutil.copy(ff_path, modified_ff_path)

    oifs_preprocessor = OIFSPreprocessor(uoif.input_file_start_date)
    # this might be the wrong start date for progvar but does not matter for the test
    progvar = xr.open_mfdataset(
        data_dir / "progvar.nc", preprocess=oifs_preprocessor.preprocess
    )
    progvar_final_time_step = uoif.extract_final_time_step(progvar)

    ff = xr.open_mfdataset(ff_path, preprocess=oifs_preprocessor.preprocess)
    final_time_step_index = uoif.find_time_index_in_file(ff, progvar_final_time_step)

    uoif.update_oifs_input_file_from_progvar(modified_ff_path, progvar)

    modified_ff = xr.open_mfdataset(
        modified_ff_path, preprocess=oifs_preprocessor.preprocess
    )

    assert (
        ff.t.isel(time=final_time_step_index)
        != modified_ff.t.isel(time=final_time_step_index)
    ).any()
    assert (
        modified_ff.u.isel(time=final_time_step_index) == progvar_final_time_step.u
    ).all()
    assert (
        ff.t.isel(time=final_time_step_index - 1)
        == modified_ff.t.isel(time=final_time_step_index - 1)
    ).all()
    assert (
        ff.q.isel(time=final_time_step_index + 1)
        == modified_ff.q.isel(time=final_time_step_index + 1)
    ).all()

    modified_ff.close()
    modified_ff_path.unlink()
