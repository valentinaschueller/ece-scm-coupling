from pathlib import Path

import numpy as np
import proplot as pplt
import xarray as xr

import helpers as hlp
import plotting as aplt


def generate_experiments(
    exp_prefix: str, dt_cpl: int, dt_ifs: int, dt_nemo: int, cpl_scheme: int
):
    exp_setups = []
    legwwms_vals = ["T", "F"]
    for legwwms_val in legwwms_vals:
        dct = {
            "exp_id": f"{exp_prefix}{legwwms_val}",
            "dt_cpl": dt_cpl,
            "dt_nemo": dt_nemo,
            "dt_ifs": dt_ifs,
            "cpl_scheme": cpl_scheme,
            "ifs_legwwms": legwwms_val,
        }
        exp_setups.append(dct)
    return exp_setups


def load_datasets(setup: str, exp_ids: list):
    run_directories = [Path(f"{setup}/{exp_id}") for exp_id in exp_ids]
    oifs_preprocessor = aplt.OIFSPreprocessor(
        np.datetime64("2014-07-01"), np.timedelta64(-7, "h")
    )
    nemo_preprocessor = aplt.NEMOPreprocessor(np.timedelta64(-7, "h"))
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
    setup = "PAPA"
    oifs_progvars, oifs_diagvars, nemo_t_grids = load_datasets(setup, exp_ids)

    colors = ["k", "C8"]
    labels = ["GWD = TRUE", "GWD = FALSE"]
    linestyles = ["-", ":"]
    alpha = 1

    fig, axs = pplt.subplots(nrows=3, ncols=1, spany=False)
    fig.set_size_inches(15, 10)
    fig.suptitle("Impact of non-orographic wave drag scheme", y=0.95, size=14)

    aplt.create_atm_temps_plot(axs[0], oifs_progvars, colors, alpha, labels, linestyles)
    aplt.create_oce_ssts_plot(axs[1], nemo_t_grids, colors, alpha, labels, linestyles)
    aplt.create_atm_ssws_plot(axs[2], oifs_diagvars, colors, alpha, labels, linestyles)
    fig.savefig(
        f"plots/legwwms_impact/{setup}_{exp_ids[0][:-1]}.pdf",
        bbox_inches="tight",
    )


dt_cpl = 3600
dt_ifs = 900
dt_nemo = 1800

cpl_scheme = 0
exp_prefix = "GWD"

experiments = generate_experiments(exp_prefix, dt_cpl, dt_ifs, dt_nemo, cpl_scheme)
print(experiments)

config_template = hlp.get_template("config-run.xml.j2")
destination = Path("../aoscm/runtime/scm-classic/PAPA")

for experiment in experiments:
    hlp.render_config_xml(destination, config_template, experiment)
    print(f"Config: {experiment['exp_id']}")
    hlp.run_model()
exp_ids = [experiment["exp_id"] for experiment in experiments]
print("Creating plots")
create_and_save_plots(exp_ids)
print("Plots created!")
