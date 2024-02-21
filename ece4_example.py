import pandas as pd

import user_context as context
from setup_experiment import set_experiment_date_properties, set_experiment_input_files
from utils.helpers import AOSCM, reduce_output
from utils.templates import render_config_xml

cpl_scheme = 0
dt_cpl = 3600
dt_ifs = 900
dt_nemo = 900
max_iters = 20

start_date = pd.Timestamp("2014-07-01")
simulation_duration = pd.Timedelta(12, "hours")
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
    context.platform,
)


if __name__ == "__main__":

    experiment["exp_id"] = f"TEST"
    experiment["cpl_scheme"] = cpl_scheme
    print(f"Config: {experiment['exp_id']}")
    render_config_xml(
        context.runscript_dir, context.config_run_template, experiment
    )
    aoscm.run_coupled_model()
    # reduce_output(
    #     context.output_dir / experiment["exp_id"], keep_debug_output=False
    # )
