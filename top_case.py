import pandas as pd

from context import Context
from schwarz_coupling import SchwarzCoupling
from setup_experiment import set_experiment_date_properties
from utils.helpers import AOSCM, reduce_output
from utils.templates import render_config_xml

context = Context(
    platform="pc-gcc-openmpi",
    model_version=3,
    model_dir="/home/valentina/dev/aoscm/ece3-scm",
    output_dir="/home/valentina/dev/aoscm/scm_rundir",
    template_dir="/home/valentina/dev/aoscm/scm_rundir/templates",
    plotting_dir="/home/valentina/dev/aoscm/scm_rundir/plots",
    data_dir="/home/valentina/dev/aoscm/initial_data/top_case",
)

cpl_schemes = [0, 1, 2]
dt_cpl = 900
dt_ifs = 900
dt_nemo = 900
max_iters = 30
exp_prefix = "WAI"

start_date = pd.Timestamp("2020-04-16")
simulation_duration = pd.Timedelta(2, "days")
ifs_input_start_date = pd.Timestamp("2020-04-12")
ifs_input_freq = pd.Timedelta(1, "hours")

experiment = {
    "dt_cpl": dt_cpl,
    "dt_nemo": dt_nemo,
    "dt_ifs": dt_ifs,
    "ifs_leocwa": "F",
    "ifs_lecumf": "F",
    "ifs_levels": 137,
}
set_experiment_date_properties(
    experiment, start_date, simulation_duration, ifs_input_start_date, ifs_input_freq
)
nemo_input_file = context.nemo_input_files_dir / "init_C1D_TOP.nc"
lim_input_file = context.lim_input_files_dir / "ice_restart_csv_16_tskin_Kelvin.nc"
oifs_input_file = context.ifs_input_files_dir / "MOS6merged.nc"
oasis_rstas = context.rstas_dir / "rstas_2020-04-16.nc"
oasis_rstos = context.rstos_dir / "rstos_2020-04-16.nc"

assert nemo_input_file.exists()
assert oifs_input_file.exists()
assert oasis_rstas.exists()
assert oasis_rstos.exists()
assert lim_input_file.exists()

experiment["nem_input_file"] = nemo_input_file
experiment["lim_input_file"] = lim_input_file
experiment["ifs_input_file"] = oifs_input_file
experiment["oasis_rstas"] = oasis_rstas
experiment["oasis_rstos"] = oasis_rstos

aoscm = AOSCM(context)


def run_baseline_experiment():
    cpl_scheme = 0
    experiment["exp_id"] = f"{exp_prefix}{cpl_scheme}"
    experiment["cpl_scheme"] = cpl_scheme
    print(f"Config: {experiment['exp_id']}")
    render_config_xml(context, experiment)
    aoscm.run_coupled_model()


def run_naive_experiments():
    for cpl_scheme in cpl_schemes:
        experiment["exp_id"] = f"{exp_prefix}{cpl_scheme}"
        experiment["cpl_scheme"] = cpl_scheme
        print(f"Config: {experiment['exp_id']}")
        render_config_xml(context, experiment)
        aoscm.run_coupled_model()
        reduce_output(
            context.output_dir / experiment["exp_id"], keep_debug_output=False
        )


def run_parallel_schwarz():
    experiment["exp_id"] = f"{exp_prefix}S"
    experiment["cpl_scheme"] = 0
    schwarz_exp = SchwarzCoupling(experiment)
    schwarz_exp.run(max_iters)


def run_atmosphere_only():
    cpl_scheme = 0
    experiment["exp_id"] = f"{exp_prefix}{cpl_scheme}"
    experiment["cpl_scheme"] = cpl_scheme
    render_config_xml(context, experiment)
    aoscm.run_atmosphere_only()
    reduce_output(context.output_dir / experiment["exp_id"], keep_debug_output=False)


if __name__ == "__main__":
    # run_atmosphere_only()
    run_naive_experiments()
    # run_baseline_experiment()

    run_parallel_schwarz()
