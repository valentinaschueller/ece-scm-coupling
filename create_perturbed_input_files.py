import shutil
from pathlib import Path

import pandas as pd
import xarray as xr

import utils.helpers as hlp
import utils.input_file_names as ifn
from context import Context
from utils.files import OIFSPreprocessor
from utils.templates import render_config_xml
from utils.update_oifs_input_file import update_oifs_input_file_from_progvar

# ------------------------------------------------
# User input starts here:
# ------------------------------------------------
context = Context(
    platform="pc-gcc-openmpi",
    model_version=3,
    model_dir="/home/valentina/dev/aoscm/ece3-scm",
    output_dir="/home/valentina/dev/aoscm/scm_rundir",
    template_dir="/home/valentina/dev/aoscm/scm_rundir/templates",
    plotting_dir="/home/valentina/dev/aoscm/scm_rundir/plots",
    data_dir="/home/valentina/dev/aoscm/initial_data/nwp",
)

input_file_start_date = pd.Timestamp("2014-07-01")
final_start_date = pd.Timestamp("2014-07-26 18:00")
input_file_freq = pd.Timedelta(6, "h")

original_input_file = ifn.get_oifs_input_file(context.data_dir / "oifs", "era")

# Experiment settings
exp_id = "PERT"

# time stepping settings
dt_cpl = 3600
dt_nemo = 1200
dt_ifs = 720
ifs_nradfr = -1
simulation_duration = pd.Timedelta(2, "day")

# other parameterization settings
ifs_leocwa = "F"

run_directory = context.output_dir / exp_id

# ------------------------------------------------
# End of user input.
# ------------------------------------------------

start_dates = pd.date_range(
    input_file_start_date, final_start_date, freq=input_file_freq
)

# basic experiment dictionary, settings shared for each run
experiment = {
    "exp_id": exp_id,
    "dt_cpl": dt_cpl,
    "dt_nemo": dt_nemo,
    "dt_ifs": dt_ifs,
    "ifs_leocwa": ifs_leocwa,
    "ifs_nradfr": ifs_nradfr,
    "ifs_input_file": original_input_file,
}

coupling_scheme_mapping = {
    0: "par",
    1: "atm",
    2: "oce",
}


def create_input_file_copies(original_input_file: Path) -> list[Path]:
    """Create appropriately named copies of the original input file"""
    copied_input_files = []
    for coupling_scheme_string in coupling_scheme_mapping.values():
        copied_input_file = shutil.copy(
            original_input_file,
            ifn.get_oifs_input_file(
                context.data_dir / "oifs", coupling_scheme_string, False
            ),
        )
        copied_input_files.append(copied_input_file)
    return copied_input_files


def update_experiment_date_properties(
    experiment: dict,
    start_date: pd.Timestamp,
    simulation_duration: pd.Timedelta,
    input_file_start_date: pd.Timestamp,
    input_file_freq: pd.Timedelta,
) -> None:
    """
    add/update keys in the experiment dictionary that are related to start and end dates of the simulation:
    - run_start_date/run_end_date
    - nem_input_file
    - ifs_nstrtini
    """
    experiment["run_start_date"] = start_date

    nemo_input_file = ifn.get_nemo_input_file(context.nemo_input_files_dir, start_date)
    experiment["nem_input_file"] = nemo_input_file

    end_date = start_date + simulation_duration
    experiment["run_end_date"] = end_date

    nstrtini = hlp.compute_nstrtini(
        start_date, input_file_start_date, int(input_file_freq.seconds / 3600)
    )
    experiment["ifs_nstrtini"] = nstrtini

    rstas_file = context.rstas_dir / ifn.get_rstas_name(start_date, "era")
    if not rstas_file.exists():
        raise ValueError(f"{rstas_file} does not exist!")
    rstos_file = context.rstos_dir / ifn.get_rstos_name(start_date)
    if not rstos_file.exists():
        raise ValueError(f"{rstos_file} does not exist!")
    experiment["oasis_rstas"] = rstas_file
    experiment["oasis_rstos"] = rstos_file


def create_perturbed_input_files() -> None:
    copied_input_files = create_input_file_copies(original_input_file)

    for start_date in start_dates:
        oifs_preprocessor = OIFSPreprocessor(start_date)

        update_experiment_date_properties(
            experiment,
            start_date,
            simulation_duration,
            input_file_start_date,
            input_file_freq,
        )

        for coupling_scheme in coupling_scheme_mapping.keys():
            experiment["cpl_scheme"] = coupling_scheme

            # render template and run model
            render_config_xml(context, experiment)
            hlp.run_model()

            progvar = xr.open_mfdataset(
                run_directory / "progvar.nc", preprocess=oifs_preprocessor.preprocess
            )
            update_oifs_input_file_from_progvar(
                copied_input_files[coupling_scheme], progvar
            )

    shutil.rmtree(run_directory)


if __name__ == "__main__":

    create_perturbed_input_files()
