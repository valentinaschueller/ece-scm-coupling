from pathlib import Path

import matplotlib.pyplot as plt

import helpers as hlp
from plotting import (
    create_atm_ssws_plot,
    create_atm_temps_plot,
    create_oce_ssts_plot,
    create_oce_ssws_plot,
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
# change the following two lines to switch between experiment A and B
dt_cpl = dt_cpl_B
exp_type = "B"


def generate_exp_ids(exp_prefix: str, exp_type: str, dt_cpl=list):
    ndts = len(dt_cpl)
    exp_setups = []
    if exp_type == "A":
        dt_ifs = dt_cpl
        dt_nemo = dt_cpl
    else:
        smallest_dt = dt_cpl[-1]
        dt_ifs = [smallest_dt] * ndts
        dt_nemo = dt_ifs
    for i in range(ndts):
        exp_setups_i = []
        for j in range(3):
            dct = {
                "exp_id": f"{exp_prefix}{exp_type}{i}{j}",
                "dt_cpl": dt_cpl[i],
                "dt_nemo": dt_nemo[i],
                "dt_ifs": dt_ifs[i],
                "cpl_scheme": j,
                "ifs_leocwa": "F",
            }
            exp_setups_i.append(dct)
        exp_setups.append(exp_setups_i)
    return exp_setups


def load_variables(setup: str, exp_ids: list):
    oce_t_files = [f"{setup}/{exp_id}/{exp_id}*_T.nc" for exp_id in exp_ids]
    atm_prog_files = [f"{setup}/{exp_id}/progvar.nc" for exp_id in exp_ids]
    atm_diag_files = [f"{setup}/{exp_id}/diagvar.nc" for exp_id in exp_ids]
    atm_temps = [
        hlp.load_cube(atm_prog_file, "Temperature") for atm_prog_file in atm_prog_files
    ]
    oce_ssts = [
        hlp.load_cube(oce_t_file, "Sea Surface temperature")
        for oce_t_file in oce_t_files
    ]
    atm_ssws = [
        hlp.load_cube(atm_diag_file, "Surface SW Radiation")
        for atm_diag_file in atm_diag_files
    ]
    oce_ssws = [
        hlp.load_cube(oce_t_file, "Shortwave Radiation") for oce_t_file in oce_t_files
    ]
    return atm_temps, oce_ssts, atm_ssws, oce_ssws


def create_and_save_plots(exp_ids):
    setup = "PAPA"
    atm_temps, oce_ssts, atm_ssws, oce_ssws = load_variables(setup, exp_ids)

    colors = ["k", "C8", "C9"]
    labels = ["parallel", "atm-first", "oce-first"]
    alpha = 0.7
    linestyles = ["-", "-", "-"]

    fig, axs = plt.subplots(4, 1)
    fig.set_size_inches(15, 10)
    fig.suptitle(f"{exp_ids[0]}, {exp_ids[1]}, {exp_ids[2]}", y=0.95, size=14)

    create_atm_temps_plot(axs[0], atm_temps, colors, alpha, labels, linestyles)
    create_oce_ssts_plot(axs[1], oce_ssts, colors, alpha, labels, linestyles)
    create_atm_ssws_plot(axs[2], atm_ssws, colors, alpha, labels, linestyles)
    create_oce_ssws_plot(axs[3], oce_ssws, colors, alpha, labels, linestyles)
    fig.savefig(
        f"plots/cpl_conv/cpl_scheme_conv_{setup}_{exp_ids[0][:-1]}.pdf",
        bbox_inches="tight",
    )


exp_setups = generate_exp_ids(exp_prefix, exp_type, dt_cpl)
print(exp_setups)

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
