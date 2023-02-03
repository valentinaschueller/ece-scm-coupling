import numpy as np
import xarray as xr


class OIFSPreprocessor:
    """Preprocessor for Output Data from the OpenIFS SCM."""

    def __init__(self, origin: np.datetime64, time_shift: np.timedelta64):
        self.origin = origin
        self.time_shift = time_shift

    def preprocess(self, ds: xr.Dataset) -> xr.Dataset:
        fixed_ds = ds.assign_coords(
            {"time": self.origin + ds.time.data + self.time_shift}
        )
        return fixed_ds


class NEMOPreprocessor:
    """Preprocessor for Output Data from the NEMO SCM."""

    def __init__(self, time_shift: np.timedelta64):
        self.time_shift = time_shift

    def preprocess(self, ds: xr.Dataset) -> xr.Dataset:
        fixed_ds = ds.assign_coords(
            {"time_counter": ds.time_counter.data + self.time_shift}
        )
        return fixed_ds


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
            oce_t_grid.sosstsst[:, 1, 1],
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
