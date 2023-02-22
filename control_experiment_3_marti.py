import pandas as pd

import user_context as context
from schwarz_coupling import SchwarzCoupling
from setup_experiment import set_experiment_date_properties, set_experiment_input_files
from utils.helpers import AOSCM, reduce_output
from utils.templates import render_config_xml

cpl_schemes = [0, 1, 2]
dt_cpl = 14400
dt_ifs = 300
dt_nemo = 1800
max_iters = 60
exp_prefix = "M4S"

start_date = pd.Timestamp("2014-07-01")
simulation_duration = pd.Timedelta(5, "days")
ifs_input_start_date = pd.Timestamp("2014-07-01")
ifs_input_freq = pd.Timedelta(6, "hours")


experiment = {
    "dt_cpl": dt_cpl,
    "dt_nemo": dt_nemo,
    "dt_ifs": dt_ifs,
    "ifs_leocwa": "F",
    "ifs_nradfr": -1,
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
    for cpl_scheme in cpl_schemes:
        experiment["exp_id"] = f"{exp_prefix}{cpl_scheme}"
        experiment["cpl_scheme"] = cpl_scheme
        print(f"Config: {experiment['exp_id']}")
        render_config_xml(
            context.runscript_dir, context.config_run_template, experiment
        )
        aoscm.run_coupled_model()
        reduce_output(
            context.output_dir / experiment["exp_id"], keep_debug_output=False
        )


def run_schwarz_experiments():
    cpl_scheme = 0
    experiment["cpl_scheme"] = cpl_scheme
    experiment["exp_id"] = f"{exp_prefix}{cpl_scheme}"
    schwarz_exp = SchwarzCoupling(experiment_dict=experiment)
    schwarz_exp.run(max_iters)


if __name__ == "__main__":

    run_naive_experiments()

    run_schwarz_experiments()
