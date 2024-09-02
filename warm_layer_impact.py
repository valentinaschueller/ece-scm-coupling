import numpy as np
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


def load_datasets(exp_ids: list):
    run_directories = [context.output_dir / exp_id for exp_id in exp_ids]
    oifs_preprocessor = OIFSPreprocessor(start_date, np.timedelta64(-7, "h"))
    nemo_preprocessor = NEMOPreprocessor(start_date, np.timedelta64(-7, "h"))
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
    oifs_progvars, oifs_diagvars, nemo_t_grids = load_datasets(exp_ids)

    colors = ["k", "C8"]
    labels = ["OCWA = TRUE", "OCWA = FALSE"]
    linestyles = ["-", ":"]
    alpha = 1

    fig, axs = pplt.subplots(nrows=3, ncols=1, spany=False)
    fig.set_size_inches(15, 10)
    fig.suptitle("Impact of ocean warm layer parameterization", y=0.95, size=14)

    uplt.create_atm_temps_plot(axs[0], oifs_progvars, colors, alpha, labels, linestyles)
    uplt.create_oce_ssts_plot(axs[1], nemo_t_grids, colors, alpha, labels, linestyles)
    uplt.create_atm_ssws_plot(axs[2], oifs_diagvars, colors, alpha, labels, linestyles)
    fig.savefig(
        f"plots/leocwa_impact/{exp_ids[0][:-1]}.pdf",
        bbox_inches="tight",
    )


start_date = pd.Timestamp("2014-07-01")
simulation_duration = pd.Timedelta("4D")
ifs_input_file_start_date = pd.Timestamp("2014-07-01")
ifs_input_file_freq = pd.Timedelta("6H")

dt_cpl = 3600
dt_ifs = 900
dt_nemo = 1800

cpl_scheme = 0

experiment = {
    "dt_cpl": dt_cpl,
    "dt_nemo": dt_nemo,
    "dt_ifs": dt_ifs,
    "cpl_scheme": cpl_scheme,
}
set_experiment_date_properties(
    experiment,
    start_date,
    simulation_duration,
    ifs_input_file_start_date,
    ifs_input_file_freq,
)
set_experiment_input_files(experiment, start_date, "era")

exp_prefix = "OWA"

model = AOSCM(context)

leocwa_values = ["T", "F"]
exp_ids = []

for leocwa in leocwa_values:
    experiment["ifs_leocwa"] = leocwa

    exp_id = f"{exp_prefix}{leocwa}"
    exp_ids.append(exp_id)
    experiment["exp_id"] = exp_id

    render_config_xml(context, experiment)

    print(f"Config: {experiment['exp_id']}")
    model.run_coupled_model(print_time=False, schwarz_correction=False)

    reduce_output(context.output_dir / exp_id)

print("Creating plots")
create_and_save_plots(exp_ids)
print("Plots created!")
