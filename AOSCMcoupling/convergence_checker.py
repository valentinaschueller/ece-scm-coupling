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


def relative_error(
    iterate_1: xr.Dataset, iterate_2: xr.Dataset, reference: xr.Dataset, ord=np.inf
) -> xr.Dataset:
    """Compute e_rel = ||iterate_1 - iterate_2||_ord / ||reference||_ord.

    :param iterate_1: Dataset with 'time' coordinate.
    :type iterate_1: xr.Dataset
    :param iterate_2: Dataset with 'time' coordinate.
    :type iterate_2: xr.Dataset
    :param reference: Dataset with 'time' coordinate.
    :type reference: xr.Dataset
    :param ord: Order of the norm, defaults to np.inf
    :type ord: {non-zero int, inf, -inf, 'fro', 'nuc'}, optional
    :return: e_rel, preserving variables from the input datasets.
    :rtype: xr.Dataset
    """
    normed_delta = vector_norm(iterate_1 - iterate_2, "time", ord=ord)
    normed_reference = vector_norm(reference, "time", ord=ord)
    return normed_delta / normed_reference


def relative_criterion(
    iterate_1: xr.Dataset,
    iterate_2: xr.Dataset,
    reference: xr.Dataset,
    rel_tol: float,
    ord=np.inf,
) -> bool:
    """Determines whether ||iterate_1 - iterate_2||_ord < rel_tol * ||reference||_ord.

    :param iterate_1: Dataset with 'time' coordinate.
    :type iterate_1: xr.Dataset
    :param iterate_2: Dataset with 'time' coordinate.
    :type iterate_2: xr.Dataset
    :param reference: Dataset with 'time' coordinate.
    :type reference: xr.Dataset
    :param rel_tol: Tolerance
    :type rel_tol: float
    :param ord: Order of the norm, defaults to np.inf
    :type ord: {non-zero int, inf, -inf, 'fro', 'nuc'}, optional
    :return: Whether the above criterion is satisfied.
    :rtype: bool
    """
    normed_delta = vector_norm(iterate_1 - iterate_2, "time", ord=ord)
    normed_reference = vector_norm(reference, "time", ord=ord)
    converged_wrt_data_value = normed_delta < rel_tol * normed_reference
    converged = converged_wrt_data_value.to_numpy().all()
    return bool(converged)


class ConvergenceChecker:
    """Wrapper to compute termination criteria for Schwarz iterations."""

    def __init__(self):
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
        self.reference = None
        self.iterate_1 = None
        self.iterate_2 = None

    def _load_reference_data(self, reference_rundir: Path):
        coupling_files_reference = [
            next(reference_rundir.glob(f"{coupling_var}_*.nc"))
            for coupling_var in self.coupling_vars
        ]
        self.reference = xr.open_mfdataset(
            coupling_files_reference, preprocess=self.preprocessor.preprocess
        )

    def check_convergence(
        self,
        iterate_1_dir: Path,
        iterate_2_dir: Path,
        reference_dir: Path,
        tolerance: float,
    ):
        if self.reference is None:
            self._load_reference_data(reference_dir)

        coupling_files_1 = [
            next(iterate_1_dir.glob(f"{coupling_var}_*.nc"))
            for coupling_var in self.coupling_vars
        ]
        self.iterate_1 = xr.open_mfdataset(
            coupling_files_1, preprocess=self.preprocessor.preprocess
        )
        coupling_files_2 = [
            next(iterate_2_dir.glob(f"{coupling_var}_*.nc"))
            for coupling_var in self.coupling_vars
        ]
        self.iterate_2 = xr.open_mfdataset(
            coupling_files_2, preprocess=self.preprocessor.preprocess
        )
        conv_2_norm = relative_criterion(
            self.iterate_1,
            self.iterate_2,
            self.reference,
            tolerance,
            2,
        )
        conv_inf_norm = relative_criterion(
            self.iterate_1,
            self.iterate_2,
            self.reference,
            tolerance,
            np.inf,
        )
        return conv_2_norm, conv_inf_norm
