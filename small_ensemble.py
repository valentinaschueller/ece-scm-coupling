import shutil
from pathlib import Path

import pandas as pd

import user_context as context
from schwarz_coupling import SchwarzCoupling
from setup_experiment import set_experiment_date_properties, set_experiment_input_files
from utils.helpers import AOSCM, reduce_output, serialize_experiment_setup
from utils.templates import render_config_xml

start_dates = pd.date_range(pd.Timestamp("2014-07-03 06:00"), pd.Timestamp("2014-07-04 00:00"), freq="6H")
simulation_time = pd.Timedelta(2, "days")

ifs_input_file_start_date = pd.Timestamp("2014-07-01")
ifs_input_file_freq = pd.Timedelta(6, "hours")

dt_ifs = 720
dt_nemo = 1800
dt_cpl = 3600
ifs_nradfr = -1
ifs_leocwa = "F"
coupling_scheme = 0
exp_id = "ENSB"
run_directory = context.output_dir / exp_id

max_iters = 5

ensemble_directory = context.output_dir / "ensemble_output"


sources = ["era", "par", "atm", "oce"]

if __name__ == "__main__":

    ensemble_directory.mkdir(exist_ok=True)
        

    aoscm = AOSCM(context.runscript_dir, context.ecconf_executable, context.platform)

    experiment = {
        "dt_cpl": dt_cpl,
        "dt_nemo": dt_nemo,
        "dt_ifs": dt_ifs,
        "ifs_leocwa": "F",
        "cpl_scheme": coupling_scheme,
        "exp_id": exp_id,
    }
    for start_date in start_dates:
        start_date_string = f"{start_date.date()}_{start_date.hour:02}"
        start_date_directory = ensemble_directory / start_date_string
        start_date_directory.mkdir(exist_ok=True)
        for source in sources:
            (start_date_directory / source).mkdir(exist_ok=True)

    
        set_experiment_date_properties(
            experiment,
            start_date,
            simulation_time,
            ifs_input_file_start_date,
            ifs_input_file_freq,
        )

        for source in sources:
            set_experiment_input_files(experiment, start_date, source)

            render_config_xml(
                context.runscript_dir, context.config_run_template, experiment
            )
            aoscm.run_coupled_model()
            reduce_output(run_directory, keep_debug_output=False)
            serialize_experiment_setup(experiment, run_directory)
            new_directory = start_date_directory / source / "parallel"
            run_directory.rename(new_directory)

            schwarz = SchwarzCoupling(experiment)
            schwarz.run(max_iters)
            new_directory = start_date_directory / source / "schwarz"
            for iter in range(1, max_iters + 1):
                schwarz_run_dir = Path(f"{schwarz.run_directory}_{iter}")
                schwarz_run_dir.rename(f"{new_directory}_{iter}")

    if run_directory.exists():
        shutil.rmtree(run_directory)
