from pathlib import Path

import matplotlib.pyplot as plt
import xarray as xr
from matplotlib import font_manager


def load_from_multiple_experiments(
    file_name: str,
    directories: list[str],
    preprocess: callable,
    dim=None,
) -> xr.Dataset:
    iterates = [
        xr.open_mfdataset(f"PAPA/{directory}/{file_name}", preprocess=preprocess)
        for directory in directories
    ]
    iterates = xr.concat(iterates, dim=dim)
    return iterates


def create_atm_temps_plot(
    ax_atm_temp, oifs_progvars: xr.Dataset, colors, alpha, labels, linestyles
):
    assert len(colors) == len(oifs_progvars)
    for i in range(len(colors)):
        oifs_progvar = oifs_progvars[i]
        color = colors[i]
        label = labels[i]
        linestyle = linestyles[i]
        ax_atm_temp.plot(
            oifs_progvar.t[:, 59] - 273.15,
            color=color,
            label=label,
            alpha=alpha,
            ls=linestyle,
        )
    ax_atm_temp.format(
        ylim=(8, 14),
        ylabel="T10m [°C]",
        ylocator=list(range(8, 15)),
        title="",
        xlabel="Time",
    )
    ax_atm_temp.legend(ncols=1)


def create_oce_ssts_plot(
    ax_oce_sst, oce_t_grids: xr.Dataset, colors, alpha, labels, linestyles
):
    assert len(colors) == len(oce_t_grids)
    for i in range(len(colors)):
        oce_t_grid = oce_t_grids[i]
        color = colors[i]
        label = labels[i]
        linestyle = linestyles[i]
        ax_oce_sst.plot(
            oce_t_grid.sosstsst,
            color=color,
            label=label,
            alpha=alpha,
            ls=linestyle,
        )
    ax_oce_sst.format(
        ylim=(8, 14),
        ylabel="SST [°C]",
        ylocator=list(range(8, 15)),
        title="",
        xlabel="Time",
    )


def create_atm_ssws_plot(
    ax_atm_ssw, oifs_diagvars: xr.Dataset, colors, alpha, labels, linestyles
):
    assert len(colors) == len(oifs_diagvars)
    for i in range(len(colors)):
        oifs_diagvar = oifs_diagvars[i]
        color = colors[i]
        label = labels[i]
        linestyle = linestyles[i]
        ax_atm_ssw.plot(
            oifs_diagvar.sfc_swrad,
            color=color,
            label=label,
            alpha=alpha,
            ls=linestyle,
        )
    ax_atm_ssw.format(
        ylim=(0, 1000),
        ylabel=r"Atm sfc radiation [$W m^{-2}$]",
        title="",
        xlabel="Time",
    )


def set_style():
    font_dir = Path("/home/x_valsc/tex-gyre/opentype")
    for path in font_dir.glob("*.otf"):
        font_manager.fontManager.addfont(path)
    plt.style.use("stylesheet.mpl")
