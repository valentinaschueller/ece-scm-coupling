import pandas as pd

import utils.input_file_names as ifn
from context import Context
from utils.helpers import compute_nstrtini


def set_experiment_date_properties(
    experiment: dict,
    start_date: pd.Timestamp,
    simulation_duration: pd.Timedelta,
    input_file_start_date: pd.Timestamp,
    input_file_freq: pd.Timedelta,
) -> None:
    """set keys in the experiment dictionary that are related to start and end dates of the simulation:
    - `run_start_date`/`run_end_date`
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

    end_date = start_date + simulation_duration
    experiment["run_end_date"] = end_date

    nstrtini = compute_nstrtini(
        start_date, input_file_start_date, int(input_file_freq.seconds / 3600)
    )
    experiment["ifs_nstrtini"] = nstrtini


def set_experiment_input_files(
    experiment: dict,
    context: Context,
    start_date: pd.Timestamp,
    ifs_input_file_source: str = "era",
):
    nemo_input_file = ifn.get_nemo_input_file(context.data_dir, start_date)
    experiment["nem_input_file"] = nemo_input_file.parent / nemo_input_file.name

    oifs_input_file = ifn.get_oifs_input_file(context.data_dir, ifs_input_file_source)
    experiment["ifs_input_file"] = oifs_input_file

    oasis_rstas = context.data_dir / ifn.get_rstas_name(
        start_date, ifs_input_file_source
    )
    experiment["oasis_rstas"] = oasis_rstas
    oasis_rstos = context.data_dir / ifn.get_rstos_name(start_date)
    experiment["oasis_rstos"] = oasis_rstos
