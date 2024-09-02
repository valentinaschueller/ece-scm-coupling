from pathlib import Path

import pandas as pd
import proplot as pplt
import xarray as xr

import utils.plotting as uplt
from context import Context
from setup_experiment import set_experiment_date_properties, set_experiment_input_files
from utils.files import NEMOPreprocessor, OIFSPreprocessor
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

dt_cpl_A = [
    800,
    400,
    200,
    100,
]
dt_cpl_B = [
    3200,
    1600,
    800,
    400,
    200,
    100,
]
cpl_schemes = [0, 1, 2]
exp_prefix = "V"
nradfr = 1

start_date = pd.Timestamp("2014-07-01")
simulation_duration = pd.Timedelta(4, "days")

ifs_input_start_date = pd.Timestamp("2014-07-01")
ifs_input_file_freq = pd.Timedelta(6, "hours")

# -------------------------------------------------------------------
# change the following two lines to switch between experiment A and B
dt_cpl = dt_cpl_B
exp_type = "B"
# -------------------------------------------------------------------


experiment = {
    "ifs_leocwa": "F",
    "ifs_nradfr": nradfr,
}
set_experiment_date_properties(
    experiment,
    start_date,
    simulation_duration,
    ifs_input_start_date,
    ifs_input_file_freq,
)
set_experiment_input_files(experiment, start_date, "era")


def generate_experiments(
    exp_prefix: str, experiment_type: str, dt_cpl: list, base_setup: dict
):
    ndts = len(dt_cpl)
    experiment_setups = []
    if experiment_type == "A":
        dt_ifs = dt_cpl
        dt_nemo = dt_cpl
    else:
        smallest_dt = dt_cpl[-1]
        dt_ifs = [smallest_dt] * ndts
        dt_nemo = dt_ifs
    for i in range(ndts):
        experiment_setups_i = []
        for j in range(3):
            experiment_setup = base_setup.copy()
            experiment_setup["exp_id"] = f"{exp_prefix}{experiment_type}{i}{j}"
            experiment_setup["dt_cpl"] = dt_cpl[i]
            experiment_setup["dt_nemo"] = dt_nemo[i]
            experiment_setup["dt_ifs"] = dt_ifs[i]
            experiment_setup["cpl_scheme"] = j
            experiment_setups_i.append(experiment_setup)
        experiment_setups.append(experiment_setups_i)
    return experiment_setups


def load_datasets(exp_ids: list):
    run_directories = [context.output_dir / exp_id for exp_id in exp_ids]
    oifs_preprocessor = OIFSPreprocessor(start_date, pd.Timedelta(-7, "hours"))
    nemo_preprocessor = NEMOPreprocessor(start_date, pd.Timedelta(-7, "hours"))
    oifs_progvars = [
        xr.open_mfdataset(
            run_directory / "progvar.nc", preprocess=oifs_preprocessor.preprocess
        )
        for run_directory in run_directories
    ]
    oifs_diagvars = [
        xr.open_mfdataset(
            run_directory / "diagvar.nc", preprocess=oifs_preprocessor.preprocess
        )
        for run_directory in run_directories
    ]
    nemo_t_grids = []
    for run_directory in run_directories:
        nemo_file = list(run_directory.glob("*_grid_T.nc"))[0]
        nemo_t_grids.append(
            xr.open_mfdataset(nemo_file, preprocess=nemo_preprocessor.preprocess)
        )

    return oifs_progvars, oifs_diagvars, nemo_t_grids


def create_and_save_plots(exp_ids):
    plot_directory = Path("plots/cpl_conv")
    plot_directory.mkdir(exist_ok=True)

    oifs_progvars, oifs_diagvars, nemo_t_grids = load_datasets(exp_ids)

    colors = ["m", "c", "y"]
    labels = ["parallel", "atm-first", "oce-first"]
    alpha = 1
    linestyles = ["--", ":", "-."]

    fig, axs = pplt.subplots(nrows=3, spany=False)
    fig.set_size_inches(15, 10)
    fig.suptitle(f"{exp_ids[0]}, {exp_ids[1]}, {exp_ids[2]}", y=0.95, size=14)

    uplt.create_atm_temps_plot(axs[0], oifs_progvars, colors, alpha, labels, linestyles)
    uplt.create_oce_ssts_plot(axs[1], nemo_t_grids, colors, alpha, labels, linestyles)
    uplt.create_atm_ssws_plot(axs[2], oifs_diagvars, colors, alpha, labels, linestyles)
    fig.savefig(
        plot_directory / f"cpl_scheme_conv_PAPA_{exp_ids[0][:-1]}.pdf",
        bbox_inches="tight",
    )


aoscm = AOSCM(context)

if __name__ == "__main__":

    exp_setups = generate_experiments(exp_prefix, exp_type, dt_cpl, experiment)

    for i in range(len(dt_cpl)):
        exp_ids = []
        for j in cpl_schemes:
            exp_id = exp_setups[i][j]["exp_id"]
            exp_ids.append(exp_id)
            render_config_xml(context, exp_setups[i][j])
            print(f"Config: {exp_id}")
            aoscm.run_coupled_model()
            reduce_output(context.output_dir / exp_id)
        print(f"Creating plots for exp_ids: {exp_ids}")
        create_and_save_plots(exp_ids)
        print("Plots created!")
