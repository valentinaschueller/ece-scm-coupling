import pandas as pd

from context import Context
from schwarz_coupling import SchwarzCoupling
from setup_experiment import set_experiment_date_properties, set_experiment_input_files
from utils.helpers import AOSCM, reduce_output
from utils.templates import render_config_xml

context = Context(
    platform="pc-gcc-openmpi",
    model_version=3,
    model_dir="/home/valentina/dev/aoscm/ece3-scm",
    output_dir="/home/valentina/dev/aoscm/scm_rundir",
    template_dir="/home/valentina/dev/aoscm/scm_rundir/templates",
    plotting_dir="/home/valentina/dev/aoscm/scm_rundir/plots",
    data_dir="/home/valentina/dev/aoscm/initial_data/control_experiment",
)

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

aoscm = AOSCM(context)


def run_naive_experiments():
    for freq_id, freq in nradfr_dict.items():
        experiment["ifs_nradfr"] = freq
        for cpl_scheme in cpl_schemes:
            experiment["cpl_scheme"] = cpl_scheme
            experiment["exp_id"] = f"{exp_prefix}{freq_id}{cpl_scheme}"

            print(f"Config: {experiment['exp_id']}")
            render_config_xml(context, experiment)
            aoscm.run_coupled_model()
            reduce_output(context.output_dir / experiment["exp_id"])


def run_schwarz_experiments():
    cpl_scheme = 0
    experiment["cpl_scheme"] = cpl_scheme
    for freq_id, freq in nradfr_dict.items():
        experiment["ifs_nradfr"] = freq
        experiment["exp_id"] = f"{exp_prefix}{freq_id}{cpl_scheme}"
        schwarz_exp = SchwarzCoupling(experiment, context)
        schwarz_exp.run(max_iters)


if __name__ == "__main__":

    run_naive_experiments()

    run_schwarz_experiments()
