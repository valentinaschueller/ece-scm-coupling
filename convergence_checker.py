from pathlib import Path

import numpy as np
import xarray as xr

from utils.files import OASISPreprocessor


class ConvergenceChecker:
    def __init__(self, tolerance: float = 1e-3):
        self.preprocessor = OASISPreprocessor()
        self.coupling_vars = [
            "O_OTaux1",
            "O_OTauy1",
            "O_QsrMix",
            "O_QnsMix",
            "OTotEvap",
            "OTotRain",
            "OTotSnow",
            "A_SST",
            "A_Ice_temp",
            "A_Ice_albedo",
            "A_Ice_frac",
            "A_Ice_thickness",
            "A_Snow_thickness",
        ]
        self.tolerance = tolerance

    def check_convergence(self, iterate_output: Path, reference_output: Path):
        coupling_files_reference = [
            next(reference_output.glob(f"{coupling_var}.nc"))
            for coupling_var in self.coupling_vars
        ]
        coupling_files_iterate = [
            next(iterate_output.glob(f"{coupling_var}.nc"))
            for coupling_var in self.coupling_vars
        ]
        self.reference = xr.open_mfdataset(
            coupling_files_reference, preprocess=self.preprocessor.preprocess
        )
        self.iterate = xr.open_mfdataset(
            coupling_files_iterate, preprocess=self.preprocessor.preprocess
        )
        local_convergence = self._check_local_convergence()
        amplitude_convergence = self._check_amplitude_convergence()
        return local_convergence, amplitude_convergence

    def _check_local_convergence(self) -> bool:
        converged_wrt_data_value = (
            np.abs(self.reference - self.iterate) <= 1e-3 * np.abs(self.reference)
        ).all()
        converged_successful = converged_wrt_data_value.to_array().all().load().data[()]
        return bool(converged_successful)

    def _check_amplitude_convergence(self) -> bool:
        amplitudes = np.max(self.reference) - np.min(self.reference)
        max_abs_diff = np.max(np.abs(self.reference - self.iterate))
        converged_wrt_amplitude = (max_abs_diff <= 1e-3 * amplitudes).load()
        converged_successful = converged_wrt_amplitude.to_array().all().load().data[()]
        return bool(converged_successful)
