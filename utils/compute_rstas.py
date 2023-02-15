"""
Script to calculate restart files for coupled simulation from atmosphere-only simulation and ocean initial conditions file.

Valentina Schueller <valentina.schueller@tum.de>
based on a script by Kerstin Hartung, calculation as in src/ifs/phys_ec/accnemoflux_layer.F90.
"""

import argparse
from pathlib import Path

import numpy as np
import xarray as xr


def compute_rstas(
    run_directory: Path, existing_rstas_file: Path, out_file: Path
) -> None:
    """create a new restart file using OIFS output, with the structure of an existing restart file.

    :param run_directory: (relative) path to directory of previous OpenIFS-SCM simulation. Must contain a file `diagvar.nc`.
    :type run_directory: Path
    :param existing_rstas_file: (relative) path to existing rstas.nc file, to copy its structure.
    :type existing_rstas_file: Path
    :param out_file: where to put the new restart file.
    :type out_file: Path
    """

    diagvar = xr.open_dataset(run_directory / "diagvar.nc").isel(time=0)

    # open default rstas to get file structure
    rstas = xr.open_dataset(existing_rstas_file)

    # define some constants, from src/surf/module/suscst_mod.F90
    latent_heat_condensation = 2.5008 * 10**6
    latent_heat_deposition = 2.8345 * 10**6
    sigma, cp_dry = _compute_radiation_constants()

    _compute_wind_stress(rstas, diagvar)
    _compute_solar_heat_flux(rstas, diagvar)
    _compute_nonsolar_heat_flux(rstas, diagvar)
    _compute_evaporation(
        rstas, diagvar, latent_heat_condensation, latent_heat_deposition
    )
    _compute_precipitation(rstas, diagvar)
    _compute_dQns_dt(rstas, diagvar, sigma, cp_dry, latent_heat_deposition)

    rstas.to_netcdf(out_file)


def _compute_wind_stress(rstas: xr.Dataset, diagvar: xr.Dataset) -> None:
    """computes the coupling fields: `A_TauX_oce`, `A_TauY_oce`, `A_TauX_ice`, `A_TauY_ice`

    :param rstas: dataset for coupling fields (is written to).
    :type rstas: xr.Dataset
    :param diagvar: OIFS diagvar output (is read from).
    :type diagvar: xr.Dataset
    """
    rstas.A_TauX_oce[:] = diagvar.u_sfc_strss_ti[0]
    rstas.A_TauY_oce[:] = diagvar.v_sfc_strss_ti[0]
    rstas.A_TauX_ice[:] = diagvar.u_sfc_strss_ti[1]
    rstas.A_TauY_ice[:] = diagvar.v_sfc_strss_ti[1]


def _compute_solar_heat_flux(rstas: xr.Dataset, diagvar: xr.Dataset) -> None:
    """computes the coupling fields: `A_Qs_oce`, `A_Qs_ice`, `A_Qs_mix`

    :param rstas: dataset for coupling fields (is written to).
    :type rstas: xr.Dataset
    :param diagvar: OIFS diagvar output (is read from).
    :type diagvar: xr.Dataset
    """
    rstas.A_Qs_oce[:] = diagvar.sfc_swrad
    rstas.A_Qs_ice[:] = diagvar.sfc_swrad
    rstas.A_Qs_mix[:] = diagvar.sfc_swrad


def _compute_nonsolar_heat_flux(rstas: xr.Dataset, diagvar: xr.Dataset) -> None:
    """
    computes the coupling fields: A_Qns_oce, A_Qns_ice, A_Qns_mix
    """
    rstas.A_Qns_oce[:] = (
        diagvar.sfc_sen_flx_ti[0] + diagvar.sfc_lat_flx_ti[0] + diagvar.sfc_lwrad
    )
    rstas.A_Qns_ice[:] = (
        diagvar.sfc_sen_flx_ti[1] + diagvar.sfc_lat_flx_ti[1] + diagvar.sfc_lwrad
    )
    rstas.A_Qns_mix[:] = (
        rstas.A_Qns_oce * (1 - diagvar.sea_ice_cov)
        + rstas.A_Qns_ice * diagvar.sea_ice_cov
    )


def _compute_evaporation(
    rstas: xr.Dataset,
    diagvar: xr.Dataset,
    latent_heat_condensation: float,
    latent_heat_deposition: float,
) -> None:
    """
    computes the coupling fields: A_Evap_total, A_Evap_ice
    """

    rstas.A_Evap_total[:] = (-1) * (
        (diagvar.sfc_lat_flx_ti[0] / latent_heat_condensation)
        * (1 - diagvar.sea_ice_cov)
        + (diagvar.sfc_lat_flx_ti[1] / latent_heat_deposition) * diagvar.sea_ice_cov
    )
    rstas.A_Evap_ice[:] = (-1) * diagvar.sfc_lat_flx_ti[1] / latent_heat_deposition


def _compute_precipitation(rstas: xr.Dataset, diagvar: xr.Dataset) -> None:
    """
    computes the coupling fields: A_Precip_liquid, A_Precip_solid
    """
    rstas.A_Precip_liquid[:] = diagvar.conv_rain + diagvar.stra_rain
    rstas.A_Precip_solid[:] = diagvar.conv_snow + diagvar.stra_snow


def _compute_dQns_dt(
    rstas: xr.Dataset,
    diagvar: xr.Dataset,
    sigma: float,
    cp_dry: float,
    latent_heat_deposition: float,
) -> None:
    """computes temperature sensitivity of non-solar heat fluxes (A_dQns_dT)

    :param rstas: dataset for coupling fields (is written to).
    :type rstas: xr.Dataset
    :param diagvar: OIFS diagvar output (is read from).
    :type diagvar: xr.Dataset
    :param sigma: Stefan-Boltzmann constant
    :type sigma: float
    :param cp_dry: specific heat of dry air
    :type cp_dry: float
    :param latent_heat_deposition: latent heat of deposition
    :type latent_heat_deposition: float
    """

    wind_speed = np.sqrt(diagvar.u_wind_10m**2 + diagvar.v_wind_10m**2)
    rstas.A_dQns_dT[:] = (
        (-4.0 * 0.95 * sigma * diagvar.t_skin_ti[1] ** 3)
        - (1.22 * cp_dry * 1.63 * 10 ** (-3) * wind_speed)
        + (
            latent_heat_deposition
            * 1.63
            * 10 ** (-3)
            * 11637800
            * (-5897.8)
            * wind_speed
            / diagvar.t_skin_ti[1] ** 2
            * np.exp(-5897.8 / diagvar.t_skin_ti[1])
        )
    )


def _compute_radiation_constants() -> tuple[float, float]:
    """compute the Stefan-Boltzmann constant (sigma) and specific heat of dry air (cp_dry). Same computation as in `src/surf/module/suscst_mod.F90`.

    :return: Stefan-Boltzmann constant, specific heat of dry air
    :rtype: tuple[float, float]
    """
    boltzmann_constant = 1.380658 * 10 ** (-23)
    speed_of_light = 299792458
    planck_constant = 6.6260755 * 10 ** (-34)

    stefan_boltzmann_constant = (
        2.0
        * np.pi**5
        * boltzmann_constant**4
        / (15 * speed_of_light**2 * planck_constant**3)
    )

    avogadro_constant = 6.0221367 * 10 ** (23)
    gas_constant = avogadro_constant * boltzmann_constant
    molar_mass_dry_air = 28.9644
    specific_gas_constant_dry_air = 1000.0 * gas_constant / molar_mass_dry_air

    specific_heat_dry_air = 3.5 * specific_gas_constant_dry_air
    return stefan_boltzmann_constant, specific_heat_dry_air


def _setup_parser() -> argparse.ArgumentParser:
    """set up the parser for running the Python script from the command line.

    :return: the parser which can parse the necessary CLI arguments.
    :rtype: argparse.ArgumentParser
    """

    parser = argparse.ArgumentParser(
        description="Compute an OASIS restart file for the OpenIFS-SCM from an atmosphere-only simulation and an existing restart file."
    )

    parser.add_argument(
        "run_directory",
        help="(Relative) path to directory of previous OpenIFS-SCM simulation. Must contain a file 'diagvar.nc'.",
        type=Path,
    )
    parser.add_argument(
        "existing_rstas_file",
        help="(Relative) path to existing rstas.nc file, to copy its structure.",
        type=Path,
    )
    parser.add_argument(
        "-o",
        "--out_file",
        help="Place the output into <file>. Default: run_directory/rstas_amip.nc",
        type=Path,
        default=None,
        metavar="<file>",
    )

    return parser


def _parse_command_line_arguments() -> tuple[Path, Path, Path]:
    """parse and return the CLI arguments using `argparse`.

    :return: Paths to `run_directory`, `existing_rstas_file`, `out_file`
    :rtype: tuple[Path, Path, Path]
    """
    parser = _setup_parser()

    args = parser.parse_args()
    if args.out_file is None:
        args.out_file = args.run_directory / "rstas_amip.nc"

    return args.run_directory, args.existing_rstas_file, args.out_file


if __name__ == "__main__":
    run_directory, existing_rstas_file, out_file = _parse_command_line_arguments()

    compute_rstas(run_directory, existing_rstas_file, out_file)
