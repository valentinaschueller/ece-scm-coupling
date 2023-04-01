import pandas as pd

from schwarz_coupling import SchwarzCoupling
from setup_experiment import set_experiment_date_properties, set_experiment_input_files

dt_ifs = 720
dt_nemo = 1800
dt_cpl = 3600
exp_id = "SREF"
cpl_scheme = 0

start_date = pd.Timestamp("2014-07-10 06:00:00")
source = "atm"
simulation_duration = pd.Timedelta(2, "days")
ifs_input_file_start_date = pd.Timestamp("2014-07-01")
ifs_input_file_freq = pd.Timedelta(6, "hours")

max_iters = 30

if __name__ == "__main__":

    experiment = {
        "exp_id": exp_id,
        "dt_cpl": dt_cpl,
        "dt_ifs": dt_ifs,
        "dt_nemo": dt_nemo,
        "cpl_scheme": cpl_scheme,
        "ifs_nradfr": 1,
    }
    set_experiment_date_properties(
        experiment,
        start_date,
        simulation_duration,
        ifs_input_file_start_date,
        ifs_input_file_freq,
    )
    set_experiment_input_files(experiment, start_date, source)

    schwarz_exp = SchwarzCoupling(experiment, reduce_output_after_iteration=True)
    schwarz_exp.run(max_iters)
