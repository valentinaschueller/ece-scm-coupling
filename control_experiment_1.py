import pandas as pd

import user_context as context
from utils.helpers import AOSCM
from schwarz_coupling import SchwarzCoupling
from setup_experiment import set_experiment_date_properties, set_experiment_input_files
from utils.templates import render_config_xml

cpl_schemes = [0, 1, 2]
dt_cpl = 3600
dt_ifs = 900
dt_nemo = 900
max_iters = 20
exp_prefix_naive = "C1N"
exp_prefix_schwarz = "C1S"

start_date = pd.Timestamp("2014-07-01")
simulation_duration = pd.Timedelta(4, "days")
ifs_input_start_date = pd.Timestamp("2014-07-01")
ifs_input_freq = pd.Timedelta(6, "hours")

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
    context.output_dir,
    context.platform,
)


def run_naive_experiments():
    for cpl_scheme in cpl_schemes:
        experiment["exp_id"] = f"{exp_prefix_naive}{cpl_scheme}"
        experiment["cpl_scheme"] = cpl_scheme
        print(f"Config: {experiment['exp_id']}")
        render_config_xml(
            context.runscript_dir, context.config_run_template, experiment
        )
        aoscm.run_coupled_model()
        aoscm.run_directory = context.output_dir / experiment["exp_id"]
        aoscm.reduce_output()


def run_schwarz_experiments():

    for cpl_scheme in cpl_schemes:
        experiment["exp_id"] = f"{exp_prefix_schwarz}{cpl_scheme}"
        schwarz_exp = SchwarzCoupling(experiment)
        schwarz_exp.run(max_iters)


if __name__ == "__main__":

    run_naive_experiments()

    run_schwarz_experiments()
