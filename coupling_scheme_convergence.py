import subprocess

import iris.quickplot as qplt
import jinja2
import matplotlib.pyplot as plt

import helpers as hlp
from helpers import ChangeDirectory

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
dt_cpl = dt_cpl_B
cpl_schemes = [0, 1, 2]
exp_prefix = "V"
exp_type = "B"


def get_template(template_path):
    """get Jinja2 template file"""
    search_path = ["."]

    loader = jinja2.FileSystemLoader(search_path)
    environment = jinja2.Environment(loader=loader)
    return environment.get_template(template_path)


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
            }
            exp_setups_i.append(dct)
        exp_setups.append(exp_setups_i)
    return exp_setups


def run_model():
    with ChangeDirectory("../aoscm/runtime/scm-classic/PAPA"):
        print("Running model")
        subprocess.run(
            [
                "/Users/valentina/dev/aoscm/sources/util/ec-conf/ec-conf",
                "-p",
                "valentinair",
                "config-run.xml",
            ],
            capture_output=True,
        )
        subprocess.run([], executable="./ece-scm_oifs+nemo.sh", capture_output=True)
        print("Model run successful")


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


def create_atm_temps_plot(ax_atm_temp, atm_temps, colors, alpha, labels):
    assert len(colors) == len(atm_temps)
    for i in range(len(colors)):
        atm_temp = atm_temps[i]
        color = colors[i]
        label = labels[i]
        atm_temp.convert_units("degC")
        time_coord = atm_temp.coord("time")
        time_coord.convert_units("d")
        qplt.plot(
            atm_temp[:, 59], axes=ax_atm_temp, color=color, label=label, alpha=alpha
        )
    ax_atm_temp.set_ybound(8, 14)
    ax_atm_temp.set_ylabel("T10m [°C]")
    ax_atm_temp.set_yticks(list(range(8, 15)))
    ax_atm_temp.set_xlabel("")
    ax_atm_temp.grid()
    ax_atm_temp.set_title("")
    ax_atm_temp.legend()


def create_oce_ssts_plot(ax_oce_sst, oce_ssts, colors, alpha, labels):
    assert len(colors) == len(oce_ssts)
    for i in range(len(colors)):
        oce_sst = oce_ssts[i]
        color = colors[i]
        label = labels[i]
        qplt.plot(
            oce_sst[:, 1, 1], axes=ax_oce_sst, color=color, label=label, alpha=alpha
        )
    ax_oce_sst.set_ybound(8, 14)
    ax_oce_sst.set_ylabel("SST [°C]")
    ax_oce_sst.set_yticks(list(range(8, 15)))
    ax_oce_sst.set_xlabel("")
    ax_oce_sst.grid()
    ax_oce_sst.set_title("")


def create_atm_ssws_plot(ax_atm_ssw, atm_ssws, colors, alpha, labels):
    assert len(colors) == len(atm_ssws)
    for i in range(len(colors)):
        atm_ssw = atm_ssws[i]
        color = colors[i]
        label = labels[i]
        time_coord = atm_ssw.coord("time")
        time_coord.convert_units("d")
        qplt.plot(atm_ssw[:], axes=ax_atm_ssw, color=color, label=label, alpha=alpha)
    ax_atm_ssw.set_title("")
    ax_atm_ssw.set_xlabel("")
    ax_atm_ssw.set_ylabel(r"Atm sfc radiation [$W m^{-2}$]")
    ax_atm_ssw.set_ybound(0, 800)
    ax_atm_ssw.grid()


def create_oce_ssws_plot(ax_oce_ssw, oce_ssws, colors, alpha, labels):
    assert len(colors) == len(oce_ssws)
    for i in range(len(colors)):
        oce_ssw = oce_ssws[i]
        color = colors[i]
        label = labels[i]
        qplt.plot(
            oce_ssw[:, 1, 1], axes=ax_oce_ssw, color=color, label=label, alpha=alpha
        )
    ax_oce_ssw.set_title("")
    ax_oce_ssw.set_xlabel("")
    ax_oce_ssw.set_ylabel(r"Oce sfc radiation [$W m^{-2}$]")
    ax_oce_ssw.set_ybound(0, 800)
    ax_oce_ssw.grid()


def create_and_save_plots(exp_ids):
    setup = "PAPA"
    atm_temps, oce_ssts, atm_ssws, oce_ssws = load_variables(setup, exp_ids)

    colors = ["k", "C8", "C9"]
    labels = ["parallel", "atm-first", "oce-first"]
    alpha = 0.7

    fig, axs = plt.subplots(4, 1)
    fig.set_size_inches(15, 10)
    fig.suptitle(f"{exp_ids[0]}, {exp_ids[1]}, {exp_ids[2]}", y=0.95, size=14)

    create_atm_temps_plot(axs[0], atm_temps, colors, alpha, labels)
    create_oce_ssts_plot(axs[1], oce_ssts, colors, alpha, labels)
    create_atm_ssws_plot(axs[2], atm_ssws, colors, alpha, labels)
    create_oce_ssws_plot(axs[3], oce_ssws, colors, alpha, labels)
    fig.savefig(
        f"plots/cpl_conv/cpl_scheme_conv_{setup}_{exp_ids[0][:-1]}.pdf",
        bbox_inches="tight",
    )


exp_setups = generate_exp_ids(exp_prefix, exp_type, dt_cpl)
print(exp_setups)

config_template = get_template("config-run.xml.j2")
dst_folder = "../aoscm/runtime/scm-classic/PAPA"

for i in range(len(dt_cpl)):
    for j in cpl_schemes:
        with ChangeDirectory(dst_folder):
            with open("./config-run.xml", "w") as config_out:
                config_out.write(
                    config_template.render(
                        setup_dict=exp_setups[i][j],
                    )
                )
        print(f"Config: {exp_setups[i][j]['exp_id']}")
        run_model()
    exp_ids = [exp_setups[i][j]["exp_id"] for j in cpl_schemes]
    print(f"Creating plots for exp_ids: {exp_ids}")
    create_and_save_plots(exp_ids)
    print("Plots created!")
