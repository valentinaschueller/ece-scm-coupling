import pandas as pd

import user_context as context
from schwarz_coupling import SchwarzCoupling
from setup_experiment import set_experiment_date_properties
from utils.helpers import AOSCM, reduce_output
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
nemo_input_file = context.nemo_input_files_dir / "init_PAPASTATION_2014-07-01.nc"
oifs_input_file = context.ifs_input_files_dir / "papa_2014-07_era.nc"
oasis_rstas = context.rstas_dir / "rstas_2014-07-01_00_era.nc"
oasis_rstos = context.rstos_dir / "rstos_2014-07-01.nc"

assert nemo_input_file.exists()
assert oifs_input_file.exists()
assert oasis_rstas.exists()
assert oasis_rstos.exists()

experiment["nem_input_file"] = nemo_input_file.parent / nemo_input_file.name
experiment["ifs_input_file"] = oifs_input_file
experiment["oasis_rstas"] = oasis_rstas
experiment["oasis_rstos"] = oasis_rstos

aoscm = AOSCM(
    context.runscript_dir,
    context.ecconf_executable,
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
        reduce_output(
            context.output_dir / experiment["exp_id"], keep_debug_output=False
        )


def run_schwarz_experiments():
    for cpl_scheme in cpl_schemes[:1]:
        experiment["exp_id"] = f"{exp_prefix_schwarz}{cpl_scheme}"
        experiment["cpl_scheme"] = cpl_scheme
        schwarz_exp = SchwarzCoupling(experiment)
        schwarz_exp.run(max_iters)


def run_parallel_schwarz_without_cleanup():
    experiment["exp_id"] = f"{exp_prefix_schwarz}P"
    experiment["cpl_scheme"] = 0
    schwarz_exp = SchwarzCoupling(experiment, False)
    schwarz_exp.run(max_iters)


if __name__ == "__main__":
    run_naive_experiments()

    run_schwarz_experiments()
