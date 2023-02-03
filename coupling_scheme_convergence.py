from pathlib import Path

import numpy as np
import pandas as pd
import proplot as pplt
import xarray as xr

import helpers as hlp
import plotting as aplt

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
forcing_start_date = pd.Timestamp("2014-07-01")
start_date = pd.Timestamp("2014-07-01")
end_date = start_date + pd.Timedelta(4, "days")
nstrtini = hlp.compute_nstrtini(start_date, forcing_start_date, 6)

#####################################################################
# change the following two lines to switch between experiment A and B
dt_cpl = dt_cpl_B
exp_type = "B"
#####################################################################


base_dict = {
    "ifs_leocwa": "F",
    "ifs_nradfr": nradfr,
    "ifs_nstrtini": nstrtini,
    "run_start_date": str(start_date),
    "run_end_date": str(end_date),
}


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


def load_datasets(setup: str, exp_ids: list):
    run_directories = [Path(f"{setup}/{exp_id}") for exp_id in exp_ids]
    oifs_preprocessor = aplt.OIFSPreprocessor(start_date, np.timedelta64(-7, "h"))
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
    plot_directory = Path("plots/cpl_conv")
    plot_directory.mkdir(exist_ok=True)

    setup = "PAPA"
    oifs_progvars, oifs_diagvars, nemo_t_grids = load_datasets(setup, exp_ids)

    colors = ["k", "C8", "C9"]
    labels = ["parallel", "atm-first", "oce-first"]
    alpha = 0.7
    linestyles = ["-", "-", "-"]

    fig, axs = pplt.subplots(nrows=3)
    fig.set_size_inches(15, 10)
    fig.suptitle(f"{exp_ids[0]}, {exp_ids[1]}, {exp_ids[2]}", y=0.95, size=14)

    aplt.create_atm_temps_plot(axs[0], oifs_progvars, colors, alpha, labels, linestyles)
    aplt.create_oce_ssts_plot(axs[1], nemo_t_grids, colors, alpha, labels, linestyles)
    aplt.create_atm_ssws_plot(axs[2], oifs_diagvars, colors, alpha, labels, linestyles)
    fig.savefig(
        plot_directory / f"cpl_scheme_conv_{setup}_{exp_ids[0][:-1]}.pdf",
        bbox_inches="tight",
    )


if __name__ == "__main__":

    exp_setups = generate_experiments(exp_prefix, exp_type, dt_cpl, base_dict)

    config_template = hlp.get_template("config-run.xml.j2")
    destination = Path("../aoscm/runtime/scm-classic/PAPA")

    for i in range(len(dt_cpl)):
        for j in cpl_schemes:
            hlp.render_config_xml(destination, config_template, exp_setups[i][j])
            print(f"Config: {exp_setups[i][j]['exp_id']}")
            hlp.run_model()
        exp_ids = [exp_setups[i][j]["exp_id"] for j in cpl_schemes]
        print(f"Creating plots for exp_ids: {exp_ids}")
        create_and_save_plots(exp_ids)
        print("Plots created!")
