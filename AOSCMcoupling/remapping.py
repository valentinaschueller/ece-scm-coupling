from pathlib import Path

import xarray as xr

atm_to_oce = {
    "A_TauX_oce": "O_OTaux1",
    "A_TauY_oce": "O_OTauy1",
    "A_TauX_ice": "O_ITaux1",
    "A_TauY_ice": "O_ITauy1",
    "A_Qs_mix": "O_QsrMix",
    "A_Qns_mix": "O_QnsMix",
    "A_Qs_ice": "O_QsrIce",
    "A_Qns_ice": "O_QnsIce",
    "A_Precip_liquid": "OTotRain",
    "A_Precip_solid": "OTotSnow",
    "A_Evap_total": "OTotEvap",
    "A_Evap_ice": "OIceEvap",
    "A_dQns_dT": "O_dQnsdT",
}

oce_to_atm = {
    "O_SSTSST": "A_SST",
    "O_TepIce": "A_Ice_temp",
    "O_AlbIce": "A_Ice_albedo",
    "OIceFrc": "A_Ice_frac",
    "OIceTck": "A_Ice_thickness",
    "OSnwTck": "A_Snow_thickness",
}

def _finalize_mpi_if_active():
    try:
        from mpi4py import MPI
    except ModuleNotFoundError:
        return
    if not MPI.Is_finalized():
        MPI.Finalize()


class RemapCouplerOutput:
    """
    Create input files for an upcoming Schwarz iteration.

    Fields get remapped, renamed, and their time coordinate is updated as required.
    """

    def __init__(
        self,
        read_directory: Path,
        write_directory: Path,
        coupling_scheme: int,
        dt_cpl: int,
        dt_atm: int,
        dt_oce: int,
        model_version: int,
    ) -> None:
        self.read_directory = read_directory
        self.write_directory = write_directory
        self.coupling_scheme = coupling_scheme
        self.dt_cpl = dt_cpl
        self.dt_atm = dt_atm
        self.dt_oce = dt_oce
        if model_version == 4:
            self.oifs_separator = "_OpenIFS_"
        else:
            self.oifs_separator = "_ATMIFS_"
        self.nemo_separator = "_oceanx_"

    def remap(self) -> None:
        for path in self.read_directory.glob("*.nc"):
            if self.oifs_separator in path.stem:
                self._remap_atm_to_oce(path)
            if self.nemo_separator in path.stem:
                self._remap_oce_to_atm(path)
        _finalize_mpi_if_active()

    def _remap_oce_to_atm(self, oce_file_path: Path) -> None:
        oce_var_name = oce_file_path.stem.split(self.nemo_separator)[0]
        atm_var_name = oce_to_atm.get(oce_var_name, None)
        if atm_var_name is None:
            return
        oce_da = xr.open_dataarray(oce_file_path)
        try:
            atm_da = oce_da[:, :, [4]]
        except IndexError:
            atm_da = oce_da[:, [0], [0]]
        atm_da = atm_da.rename(atm_var_name)
        if self.coupling_scheme != 2:
            atm_da = atm_da[1:]
        atm_da = atm_da.assign_coords(
            {"time": atm_da.time.data - (self.dt_cpl - self.dt_oce)}
        )
        atm_file_path = self.write_directory / f"{atm_var_name}.nc"
        atm_da.to_netcdf(atm_file_path)

    def _remap_atm_to_oce(self, atm_file_path: Path) -> None:
        atm_var_name = atm_file_path.stem.split(self.oifs_separator)[0]
        oce_var_name = atm_to_oce.get(atm_var_name, None)
        if oce_var_name is None:
            return
        atm_da = xr.open_dataarray(atm_file_path)
        oce_da = atm_da[:, 3 * [0], 3 * [0]]
        oce_da = oce_da.rename(oce_var_name)
        if self.coupling_scheme != 1:
            oce_da = oce_da[1:]
        oce_da = oce_da.assign_coords(
            {"time": oce_da.time.data - (self.dt_cpl - self.dt_atm)}
        )
        oce_file_path = self.write_directory / f"{oce_var_name}.nc"
        oce_da.to_netcdf(oce_file_path)
