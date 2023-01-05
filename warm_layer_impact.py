from pathlib import Path

import iris.quickplot as qplt
import matplotlib.pyplot as plt

import helpers as hlp


def generate_experiments(
    exp_prefix: str, dt_cpl: int, dt_ifs: int, dt_nemo: int, cpl_scheme: int
):
    exp_setups = []
    leocwa_vals = ["T", "F"]
    for leocwa_val in leocwa_vals:
        dct = {
            "exp_id": f"{exp_prefix}{leocwa_val}",
            "dt_cpl": dt_cpl,
            "dt_nemo": dt_nemo,
            "dt_ifs": dt_ifs,
            "cpl_scheme": cpl_scheme,
            "ifs_leocwa": leocwa_val,
        }
        exp_setups.append(dct)
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


def create_atm_temps_plot(ax_atm_temp, atm_temps, colors, alpha, labels, linestyles):
    assert len(colors) == len(atm_temps)
    for i in range(len(colors)):
        atm_temp = atm_temps[i]
        color = colors[i]
        label = labels[i]
        linestyle = linestyles[i]
        atm_temp.convert_units("degC")
        time_coord = atm_temp.coord("time")
        time_coord.convert_units("d")
        qplt.plot(
            atm_temp[:, 59],
            axes=ax_atm_temp,
            color=color,
            label=label,
            alpha=alpha,
            ls=linestyle,
        )
    ax_atm_temp.set_ybound(8, 14)
    ax_atm_temp.set_ylabel("T10m [°C]")
    ax_atm_temp.set_yticks(list(range(8, 15)))
    ax_atm_temp.set_xlabel("")
    ax_atm_temp.grid()
    ax_atm_temp.set_title("")
    ax_atm_temp.legend()


def create_oce_ssts_plot(ax_oce_sst, oce_ssts, colors, alpha, labels, linestyles):
    assert len(colors) == len(oce_ssts)
    for i in range(len(colors)):
        oce_sst = oce_ssts[i]
        color = colors[i]
        label = labels[i]
        linestyle = linestyles[i]
        qplt.plot(
            oce_sst[:, 1, 1],
            axes=ax_oce_sst,
            color=color,
            label=label,
            alpha=alpha,
            ls=linestyle,
        )
    ax_oce_sst.set_ybound(8, 14)
    ax_oce_sst.set_ylabel("SST [°C]")
    ax_oce_sst.set_yticks(list(range(8, 15)))
    ax_oce_sst.set_xlabel("")
    ax_oce_sst.grid()
    ax_oce_sst.set_title("")


def create_atm_ssws_plot(ax_atm_ssw, atm_ssws, colors, alpha, labels, linestyles):
    assert len(colors) == len(atm_ssws)
    for i in range(len(colors)):
        atm_ssw = atm_ssws[i]
        color = colors[i]
        label = labels[i]
        linestyle = linestyles[i]
        time_coord = atm_ssw.coord("time")
        time_coord.convert_units("d")
        qplt.plot(
            atm_ssw[:],
            axes=ax_atm_ssw,
            color=color,
            label=label,
            alpha=alpha,
            ls=linestyle,
        )
    ax_atm_ssw.set_title("")
    ax_atm_ssw.set_xlabel("")
    ax_atm_ssw.set_ylabel(r"Atm sfc radiation [$W m^{-2}$]")
    ax_atm_ssw.set_ybound(0, 800)
    ax_atm_ssw.grid()


def create_oce_ssws_plot(ax_oce_ssw, oce_ssws, colors, alpha, labels, linestyles):
    assert len(colors) == len(oce_ssws)
    for i in range(len(colors)):
        oce_ssw = oce_ssws[i]
        color = colors[i]
        label = labels[i]
        linestyle = linestyles[i]
        qplt.plot(
            oce_ssw[:, 1, 1],
            axes=ax_oce_ssw,
            color=color,
            label=label,
            alpha=alpha,
            ls=linestyle,
        )
    ax_oce_ssw.set_title("")
    ax_oce_ssw.set_xlabel("")
    ax_oce_ssw.set_ylabel(r"Oce sfc radiation [$W m^{-2}$]")
    ax_oce_ssw.set_ybound(0, 800)
    ax_oce_ssw.grid()


def create_and_save_plots(exp_ids):
    setup = "PAPA"
    atm_temps, oce_ssts, atm_ssws, oce_ssws = load_variables(setup, exp_ids)

    colors = ["k", "C8"]
    labels = ["OCWA = TRUE", "OCWA = FALSE"]
    linestyles = ["-", ":"]
    alpha = 1

    fig, axs = plt.subplots(4, 1)
    fig.set_size_inches(15, 10)
    fig.suptitle("Impact of ocean warm layer parameterization", y=0.95, size=14)

    create_atm_temps_plot(axs[0], atm_temps, colors, alpha, labels, linestyles)
    create_oce_ssts_plot(axs[1], oce_ssts, colors, alpha, labels, linestyles)
    create_atm_ssws_plot(axs[2], atm_ssws, colors, alpha, labels, linestyles)
    create_oce_ssws_plot(axs[3], oce_ssws, colors, alpha, labels, linestyles)
    fig.savefig(
        f"plots/leocwa_impact/{setup}_{exp_ids[0][:-1]}.pdf",
        bbox_inches="tight",
    )


dt_cpl = 3600
dt_ifs = 900
dt_nemo = 1800

cpl_scheme = 0
exp_prefix = "OWA"

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
