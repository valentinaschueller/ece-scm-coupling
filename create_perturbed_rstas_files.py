import shutil

import pandas as pd

import utils.input_file_names as ifn
from context import Context
from utils.compute_rstas import compute_rstas
from utils.helpers import AOSCM, compute_nstrtini
from utils.templates import render_config_xml

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

input_file_freq = pd.Timedelta(6, "h")

# Option 1 - for input files from perturbed runs:
# input_file_sources = ["par", "atm", "oce"]
# first_start_date = pd.Timestamp("2014-07-03")
# final_start_date = pd.Timestamp("2014-07-28 18:00")

# Option 2 - for existing ERA data:
input_file_sources = ["era"]
first_start_date = input_file_start_date
final_start_date = pd.Timestamp("2014-07-30 12:00")

# experiment settings
exp_id = "RSTA"

# time stepping settings
dt_cpl = 3600
dt_nemo = 1200
dt_ifs = 720
ifs_nradfr = -1
simulation_duration = pd.Timedelta(dt_ifs, "s")

# other parameterization settings
ifs_leocwa = "F"

run_directory = context.output_dir / exp_id
rstas_template = context.template_data_dir / "rstas_template.nc"

# ------------------------------------------------
# End of user input.
# ------------------------------------------------

start_dates = pd.date_range(first_start_date, final_start_date, freq=input_file_freq)

# basic experiment dictionary, settings shared for each run
experiment = {
    "exp_id": exp_id,
    "dt_cpl": dt_cpl,
    "dt_nemo": dt_nemo,
    "dt_ifs": dt_ifs,
    "ifs_leocwa": ifs_leocwa,
    "ifs_nradfr": ifs_nradfr,
    "cpl_scheme": None,
    "oasis_rstas": None,
    "oasis_rstos": None,
}

input_file_base = "papa_2014-07"


def update_experiment_date_properties(
    experiment: dict,
    start_date: pd.Timestamp,
    simulation_duration: pd.Timedelta,
    input_file_start_date: pd.Timestamp,
    input_file_freq: pd.Timedelta,
) -> None:
    """add/update keys in the experiment dictionary that are related to start and end dates of the simulation:
    - `run_start_date`/`run_end_date`
    - `nem_input_file`
    - `ifs_nstrtini`

    :param experiment: experiment dictionary
    :type experiment: dict
    :param start_date: run start date
    :type start_date: pd.Timestamp
    :param simulation_duration: simulation duration
    :type simulation_duration: pd.Timedelta
    :param input_file_start_date: start date of the OpenIFS input (forcing) file
    :type input_file_start_date: pd.Timestamp
    :param input_file_freq: frequency of data in the OpenIFS input (forcing) file
    :type input_file_freq: pd.Timedelta
    """
    experiment["run_start_date"] = start_date

    nemo_input_file = ifn.get_nemo_input_file(context.nemo_input_files_dir, start_date)
    experiment["nem_input_file"] = f"{nemo_input_file.parent}/{nemo_input_file.name}"

    end_date = start_date + simulation_duration
    experiment["run_end_date"] = end_date

    nstrtini = compute_nstrtini(
        start_date, input_file_start_date, int(input_file_freq.seconds / 3600)
    )
    experiment["ifs_nstrtini"] = nstrtini


def create_rstas_files() -> None:
    """create the atmosphere restart files from existing forcing files and save them as OASIS initial data."""
    for input_file_source in input_file_sources:
        oifs_input_file = ifn.get_oifs_input_file(
            context.ifs_input_files_dir, input_file_source
        )
        experiment["ifs_input_file"] = oifs_input_file

        for start_date in start_dates:

            update_experiment_date_properties(
                experiment,
                start_date,
                simulation_duration,
                input_file_start_date,
                input_file_freq,
            )

            render_config_xml(context, experiment)

            aoscm = AOSCM(context)
            aoscm.run_atmosphere_only()

            out_file = context.rstas_dir / ifn.get_rstas_name(
                start_date, input_file_source
            )
            compute_rstas(run_directory, rstas_template, out_file)

    shutil.rmtree(run_directory)


if __name__ == "__main__":

    create_rstas_files()
