from pathlib import Path

import pandas as pd


def get_oifs_input_file(
    directory: Path, source: str, exists_required: bool = True
) -> Path:
    oifs_input_file = directory / f"papa_2014-07_{source}.nc"
    if not exists_required:
        return oifs_input_file
    if not oifs_input_file.exists():
        raise ValueError(f"OIFS input file does not exist: {oifs_input_file}")
    return oifs_input_file


def get_nemo_input_file(directory: Path, start_date: pd.Timestamp) -> Path:
    nemo_input_file = directory / f"init_PAPASTATION_{start_date.date()}.nc"
    if not nemo_input_file.exists():
        raise ValueError(
            f"NEMO input file for selected start date does not exist: {nemo_input_file}"
        )
    return nemo_input_file


def get_rstas_name(time_stamp: pd.Timestamp, source: str) -> Path:
    """generate name of restart file, with the pattern `rstas_YYYY-MM-DD_HH_source.nc`.

    :param time_stamp: time stamp of the restart file
    :type time_stamp: pd.Timestamp
    :param source: source of the restart file (e.g., era)
    :type source: str
    :return: generated file name
    :rtype: str
    """
    date = time_stamp.date()
    hour = f"{time_stamp.time().hour:02}"

    rstas_name = f"rstas_{date}_{hour}_{source}.nc"

    return rstas_name


def get_rstos_name(time_stamp: pd.Timestamp) -> str:
    return f"rstos_{time_stamp.date()}.nc"
