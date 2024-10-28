from pathlib import Path

import numpy as np
import xarray as xr

from AOSCMcoupling.files import OASISPreprocessor


def vector_norm(x, dim, ord=None):
    return xr.apply_ufunc(
        np.linalg.norm,
        x,
        input_core_dims=[[dim]],
        kwargs={"ord": ord, "axis": -1},
        dask="allowed",
    )


class ConvergenceChecker:
    """Wrapper to compute termination criteria for Schwarz iterations."""

    def __init__(self, tolerance: float = 1e-3):
        self.preprocessor = OASISPreprocessor()
        self.coupling_vars = [
            "A_TauX_oce",
            "A_TauY_oce",
            "A_TauX_ice",
            "A_TauY_ice",
            "A_Qs_mix",
            "A_Qns_mix",
            "A_Qs_ice",
            "A_Qns_ice",
            "A_Precip_liquid",
            "A_Precip_solid",
            "A_Evap_total",
            "A_Evap_ice",
            "A_dQns_dT",
            "O_SSTSST",
            "O_TepIce",
            "O_AlbIce",
            "OIceFrc",
            "OIceTck",
            "OSnwTck",
        ]
        self.tolerance = tolerance
        self.reference = None
        self.current_iterate = None
        self.previous_iterate = None

    def load_reference_data(self, reference_rundir: Path):
        coupling_files_reference = [
            next(reference_rundir.glob(f"{coupling_var}_*.nc"))
            for coupling_var in self.coupling_vars
        ]
        self.reference = xr.open_mfdataset(
            coupling_files_reference, preprocess=self.preprocessor.preprocess
        )

    def check_convergence(self, current_iterate: Path, previous_iterate: Path):
        if self.reference is None:
            raise ValueError("Reference data needs to be loaded to check convergence!")

        current_coupling_files = [
            next(current_iterate.glob(f"{coupling_var}_*.nc"))
            for coupling_var in self.coupling_vars
        ]
        self.current_iterate = xr.open_mfdataset(
            current_coupling_files, preprocess=self.preprocessor.preprocess
        )
        previous_coupling_files = [
            next(previous_iterate.glob(f"{coupling_var}_*.nc"))
            for coupling_var in self.coupling_vars
        ]
        self.previous_iterate = xr.open_mfdataset(
            previous_coupling_files, preprocess=self.preprocessor.preprocess
        )
        conv_2_norm = self._check_convergence(ord=2)
        conv_inf_norm = self._check_convergence(ord=np.inf)
        return conv_2_norm, conv_inf_norm

    def _check_convergence(self, ord=np.inf) -> bool:
        normed_delta = vector_norm(
            self.current_iterate - self.previous_iterate, "time", ord=ord
        )
        normed_reference = vector_norm(self.reference, "time", ord=ord)
        converged_wrt_data_value = normed_delta <= self.tolerance * normed_reference
        converged_successful = converged_wrt_data_value.to_numpy().all()
        return bool(converged_successful)
