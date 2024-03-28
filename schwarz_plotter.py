from pathlib import Path
import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import xarray as xr
import top_case as experiment_runner
from utils.files import OIFSPreprocessor, NEMOPreprocessor

plt.style.use("stylesheet.mpl")

start_date = experiment_runner.start_date
time_shift = np.timedelta64(1, "h")
oifs_preprocessor = OIFSPreprocessor(start_date, time_shift)
nemo_preprocessor = NEMOPreprocessor(start_date, time_shift)

exp_id = "TOPS"
plot_folder = Path(f"plots/{exp_id}")
plot_folder.mkdir(exist_ok=True)
max_iters = experiment_runner.max_iters
alpha = 0.25

oifs_diagvars = [
    xr.open_mfdataset(
        f"PAPA/{exp_id}_{iter}/diagvar.nc", preprocess=oifs_preprocessor.preprocess
    )
    for iter in range(1, max_iters + 1)
]
oifs_progvars = [
    xr.open_mfdataset(
        f"PAPA/{exp_id}_{iter}/progvar.nc", preprocess=oifs_preprocessor.preprocess
    )
    for iter in range(1, max_iters + 1)
]
nemo_t_grids = [
    xr.open_mfdataset(
        f"PAPA/{exp_id}_{iter}/{exp_id}_*_T.nc", preprocess=nemo_preprocessor.preprocess
    )
    for iter in range(1, max_iters + 1)
]


def plot_all_iterates(da_list: list[xr.DataArray], **kwargs):
    fig, ax = plt.subplots()
    da_list[0].plot(ax=ax)

    ax.set(**kwargs)
    ax.grid()

    for da in da_list[1:]:
        ax.plot(da.time, da, alpha=alpha, color="k")

    return fig


def animate(da_list: list[xr.DataArray], **kwargs):
    fig, ax = plt.subplots()
    da_list[0].plot(ax=ax)

    ax.set(**kwargs)
    ax.grid()

    def update(frame):
        # update the line plot:
        ax.plot(
            da_list[frame + 1].time,
            da_list[frame + 1],
            color="k",
            alpha=alpha,
        )

    ani = animation.FuncAnimation(fig=fig, func=update, frames=max_iters - 1)
    return ani


def create_plots(da_list: list[xr.DataArray], file_stem: str, axis_settings: dict):
    axis_settings["xlabel"] = "Time"
    axis_settings["xmargin"] = 0.0

    fig = plot_all_iterates(da_list, **axis_settings)
    fig.savefig(f"plots/{exp_id}/{file_stem}.pdf", bbox_inches="tight")

    ani = animate(da_list, **axis_settings)
    ani.save(f"plots/{exp_id}/{file_stem}.mp4")


# %% 10m Temperature
temp_10m = [progvar.t[:, 59] - 273.15 for progvar in oifs_progvars]

axis_settings = {
    "title": "Temperature at 10m (OIFS)",
    "ylabel": "Temperature [°C]",
    "ylim": [-80, -35],
}

create_plots(temp_10m, "10t_oifs", axis_settings)


# %% Surface Sensible Heat Flux
ssh_flux = [diagvar.sfc_sen_flx for diagvar in oifs_diagvars]

axis_settings = {
    "title": "Surface Sensible Heat Flux (OIFS)",
    "ylabel": "Temperature [°C]",
    "ylim": [-80, -35],
}

create_plots(ssh_flux, "ssh_oifs", axis_settings)

# %% SST

sst = [t_grid.sosstsst for t_grid in nemo_t_grids]
axis_settings = {
    "title": "Sea Surface Temperature (NEMO)",
    "ylabel": "Temperature [°C]",
    "ylim": [-2.1, -1.3],
}
create_plots(sst, "sst_nemo", axis_settings)

# %% SSW
ssw = [oifs_diagvar.sfc_swrad for oifs_diagvar in oifs_diagvars]

axis_settings = {
    "title": "Surface SW Radiation (OIFS)",
    "ylabel": "Radiative Flux $[W m^{-2}]$",
    "ylim": [0, 80],
}

create_plots(ssw, "ssw_oifs", axis_settings)
