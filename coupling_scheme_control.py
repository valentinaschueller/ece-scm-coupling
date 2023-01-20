import matplotlib.pyplot as plt

import helpers as hlp
from helpers import ChangeDirectory, get_template
from plotting import (
    create_atm_ssws_plot,
    create_atm_temps_plot,
    create_oce_ssts_plot,
    create_oce_ssws_plot,
)


def generate_experiments(
    exp_prefix: str, dt_cpl: int, dt_ifs: int, dt_nemo: int, cpl_schemes: list
):
    exp_setups = []
    for cpl_scheme in cpl_schemes:
        dct = {
            "exp_id": f"{exp_prefix}{cpl_scheme}",
            "dt_cpl": dt_cpl,
            "dt_nemo": dt_nemo,
            "dt_ifs": dt_ifs,
            "cpl_scheme": cpl_scheme,
            "ifs_leocwa": "F",
        }
        exp_setups.append(dct)
    return exp_setups


dt_cpl = 3600
cpl_schemes = [0, 1, 2]
exp_prefix = "CPL"
dt_ifs = 900
dt_nemo = 900
experiments = generate_experiments(exp_prefix, dt_cpl, dt_ifs, dt_nemo, cpl_schemes)

config_template = get_template("config-run.xml.j2")
dst_folder = "../aoscm/runtime/scm-classic/PAPA"


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
        f"plots/cpl_control/cpl_scheme_control.pdf",
        bbox_inches="tight",
    )


for experiment in experiments:
    with ChangeDirectory(dst_folder):
        with open("./config-run.xml", "w") as config_out:
            config_out.write(
                config_template.render(
                    setup_dict=experiment,
                )
            )
    print(f"Config: {experiment['exp_id']}")
    hlp.run_model()
create_and_save_plots([experiment["exp_id"] for experiment in experiments])
