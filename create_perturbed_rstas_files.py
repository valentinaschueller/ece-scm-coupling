import shutil

import pandas as pd

import user_context as context
from utils.compute_rstas import compute_rstas
from utils.helpers import AOSCM, compute_nstrtini
from utils.templates import render_config_xml

# ------------------------------------------------
# User input starts here:
# ------------------------------------------------


input_file_start_date = pd.Timestamp("2014-07-01")

first_start_date = pd.Timestamp("2014-07-03")
final_start_date = pd.Timestamp("2014-07-03 12:00")
# final_start_date = pd.Timestamp("2014-07-26 18:00")
input_file_freq = pd.Timedelta(6, "h")


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
}

input_file_base = "papa_2014-07"
input_file_sources = ["era", "par", "atm", "oce"]


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
    experiment[
        "nem_input_file"
    ] = f"{context.nemo_input_files_dir.name}/init_PAPASTATION_{start_date.date()}.nc"

    end_date = start_date + simulation_duration
    experiment["run_end_date"] = end_date

    nstrtini = compute_nstrtini(
        start_date, input_file_start_date, int(input_file_freq.seconds / 3600)
    )
    experiment["ifs_nstrtini"] = nstrtini


def generate_rstas_name(start_date: pd.Timestamp, source: str) -> str:
    date = start_date.date()
    hour = f"{start_date.time().hour:02}"

    rstas_name = f"rstas_{date}_{hour}_{source}.nc"

    return rstas_name


def create_perturbed_rstas_files() -> None:
    for input_file_source in input_file_sources:
        input_file_name = f"{input_file_base}_{input_file_source}.nc"
        experiment[
            "ifs_input_file"
        ] = f"{context.ifs_input_files_dir.name}/{input_file_name}"

        for start_date in start_dates:

            update_experiment_date_properties(
                experiment,
                start_date,
                simulation_duration,
                input_file_start_date,
                input_file_freq,
            )

            render_config_xml(
                context.runscript_dir, context.config_run_template, experiment
            )

            aoscm = AOSCM(
                context.runscript_dir,
                context.ecconf_executable,
                run_directory,
                context.platform,
            )
            aoscm.run_atmosphere_only()

            out_file = context.rstas_dir / generate_rstas_name(
                start_date, input_file_source
            )
            compute_rstas(run_directory, rstas_template, out_file)

    shutil.rmtree(run_directory)


if __name__ == "__main__":

    create_perturbed_rstas_files()
