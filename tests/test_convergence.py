import numpy as np
import xarray as xr

from AOSCMcoupling.convergence_checker import relative_criterion, vector_norm


def test_vector_norm():
    arr = np.random.rand(5)
    da = xr.DataArray(arr)
    assert np.isclose(np.linalg.norm(arr), vector_norm(da, "dim_0"))
    assert np.isclose(np.linalg.norm(arr, np.inf), vector_norm(da, "dim_0", np.inf))


def test_relative_criterion():
    arr_1 = np.random.rand(5)
    arr_2 = arr_1 * (1 + 1e-4)
    da_1 = xr.DataArray(arr_1, dims="time")
    da_2 = xr.DataArray(arr_2, dims="time")
    assert relative_criterion(da_1, da_2, da_1, 1e-3)
    assert not relative_criterion(da_1, da_2, da_1, 1e-5)
