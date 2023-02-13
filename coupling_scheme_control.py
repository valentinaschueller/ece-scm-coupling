from pathlib import Path

import numpy as np
import pandas as pd
import proplot as pplt
import xarray as xr

import utils.helpers as hlp
import utils.plotting as uplt
from utils.templates import get_template, render_config_xml

dt_cpl = 3600
cpl_schemes = [0, 1, 2]
exp_prefix = "CPL"
dt_ifs = 900
dt_nemo = 900
nradfr = 1
forcing_start_date = pd.Timestamp("2014-07-01")
start_date = pd.Timestamp("2014-07-01")
end_date = start_date + pd.Timedelta(4, "days")
nstrtini = hlp.compute_nstrtini(start_date, forcing_start_date, 6)

base_dict = {
    "dt_cpl": dt_cpl,
    "dt_nemo": dt_nemo,
    "dt_ifs": dt_ifs,
    "ifs_leocwa": "F",
    "ifs_nradfr": nradfr,
    "ifs_nstrtini": nstrtini,
    "run_start_date": str(start_date),
    "run_end_date": str(end_date),
}


def generate_experiments(exp_prefix: str, cpl_schemes: list, base_setup: dict):
    experiment_setups = []
    for cpl_scheme in cpl_schemes:
        experiment_setup = base_setup.copy()
        experiment_setup["exp_id"] = f"{exp_prefix}{cpl_scheme}"
        experiment_setup["cpl_scheme"] = cpl_scheme
        experiment_setups.append(experiment_setup)
    return experiment_setups


def load_datasets(setup: str, exp_ids: list):
    run_directories = [Path(f"{setup}/{exp_id}") for exp_id in exp_ids]
    oifs_preprocessor = uplt.OIFSPreprocessor(start_date, np.timedelta64(-7, "h"))
    nemo_preprocessor = uplt.NEMOPreprocessor(np.timedelta64(-7, "h"))
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
    plot_directory = Path("plots/cpl_control")
    plot_directory.mkdir(exist_ok=True)

    setup = "PAPA"
    oifs_progvars, oifs_diagvars, nemo_t_grids = load_datasets(setup, exp_ids)

    colors = ["k", "C8", "C9"]
    labels = ["parallel", "atm-first", "oce-first"]
    alpha = 1
    linestyles = ["--", ":", "-."]

    fig, axs = pplt.subplots(nrows=3)
    fig.set_size_inches(15, 10)
    fig.suptitle(f"{exp_ids[0]}, {exp_ids[1]}, {exp_ids[2]}", y=0.95, size=14)

    uplt.create_atm_temps_plot(axs[0], oifs_progvars, colors, alpha, labels, linestyles)
    uplt.create_oce_ssts_plot(axs[1], nemo_t_grids, colors, alpha, labels, linestyles)
    uplt.create_atm_ssws_plot(axs[2], oifs_diagvars, colors, alpha, labels, linestyles)
    fig.savefig(
        plot_directory / "cpl_scheme_control.pdf",
        bbox_inches="tight",
    )


if __name__ == "__main__":
    experiments = generate_experiments(exp_prefix, cpl_schemes, base_dict)

    config_template = get_template("config-run.xml.j2")
    dst_folder = "../aoscm/runtime/scm-classic/PAPA"

    for experiment in experiments:
        render_config_xml(dst_folder, config_template, experiment)
        print(f"Config: {experiment['exp_id']}")
        hlp.run_model()
    create_and_save_plots([experiment["exp_id"] for experiment in experiments])
