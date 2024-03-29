import pandas as pd

import user_context as context
from schwarz_coupling import SchwarzCoupling
from setup_experiment import set_experiment_date_properties, set_experiment_input_files
from utils.helpers import AOSCM, reduce_output
from utils.templates import render_config_xml

dt_cpl = 3600
dt_ifs = 720
dt_nemo = 1800
max_iters = 25

cpl_schemes = [1, 2]
exp_prefix = "RA"

nradfr_dict = {
    "L": -3,
    "E": -1,
    "S": 1,
}

ifs_input_start_date = pd.Timestamp("2014-07-01")
ifs_input_freq = pd.Timedelta(6, "hours")

start_date = pd.Timestamp("2014-07-01")
simulation_duration = pd.Timedelta(4, "days")

experiment = {
    "dt_cpl": dt_cpl,
    "dt_nemo": dt_nemo,
    "dt_ifs": dt_ifs,
    "ifs_leocwa": "F",
}
set_experiment_date_properties(
    experiment, start_date, simulation_duration, ifs_input_start_date, ifs_input_freq
)
set_experiment_input_files(experiment, start_date, "era")

aoscm = AOSCM(
    context.runscript_dir,
    context.ecconf_executable,
    context.platform,
)


def run_naive_experiments():
    for freq_id, freq in nradfr_dict.items():
        experiment["ifs_nradfr"] = freq
        for cpl_scheme in cpl_schemes:
            experiment["cpl_scheme"] = cpl_scheme
            experiment["exp_id"] = f"{exp_prefix}{freq_id}{cpl_scheme}"

            print(f"Config: {experiment['exp_id']}")
            render_config_xml(
                context.runscript_dir, context.config_run_template, experiment
            )
            aoscm.run_coupled_model()
            reduce_output(context.output_dir / experiment["exp_id"])


def run_schwarz_experiments():
    cpl_scheme = 0
    experiment["cpl_scheme"] = cpl_scheme
    for freq_id, freq in nradfr_dict.items():
        experiment["ifs_nradfr"] = freq
        experiment["exp_id"] = f"{exp_prefix}{freq_id}{cpl_scheme}"
        schwarz_exp = SchwarzCoupling(experiment_dict=experiment)
        schwarz_exp.run(max_iters)


if __name__ == "__main__":

    run_naive_experiments()

    run_schwarz_experiments()
