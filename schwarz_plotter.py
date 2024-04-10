# %% Setup
from pathlib import Path
import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import xarray as xr
import top_case as experiment_runner
from utils.files import OIFSPreprocessor, NEMOPreprocessor

plt.style.use("stylesheet.mpl")


def load_iterates(
    file_name: str, preprocess: callable, max_iters: int, step: int
) -> xr.Dataset:
    swr_dim = xr.DataArray(np.arange(max_iters) + 1, dims="swr_iterate")
    iterates = [
        xr.open_mfdataset(f"PAPA/{exp_id}_{iter}/{file_name}", preprocess=preprocess)
        for iter in range(1, max_iters + 1, step)
    ]
    iterates = xr.concat(iterates, swr_dim)
    return iterates


def plot_all_iterates(da: xr.DataArray, **kwargs):
    fig, ax = plt.subplots()
    da[0].plot(ax=ax)

    ax.set(**kwargs)
    ax.grid()
    for iter in range(1, max_iters):
        ax.plot(da.time, da[iter], alpha=alpha, color="k")

    return fig


def animate(da: xr.DataArray, **kwargs):
    fig, ax = plt.subplots()
    da[0].plot(ax=ax)

    ax.set(**kwargs)
    ax.grid()

    def update(frame):
        # update the line plot:
        ax.plot(
            da[frame + 1].time,
            da[frame + 1],
            color="k",
            alpha=alpha,
        )

    ani = animation.FuncAnimation(fig=fig, func=update, frames=da.shape[0] - 1)
    return ani


def create_plots(da: xr.DataArray, file_stem: str, axis_settings: dict):
    axis_settings["xlabel"] = "Time"
    axis_settings["xmargin"] = 0.0

    fig = plot_all_iterates(da, **axis_settings)
    fig.savefig(plot_folder / f"{file_stem}.pdf", bbox_inches="tight")

    ani = animate(da, **axis_settings)
    ani.save(plot_folder / f"{file_stem}.mp4")


# %%

start_date = experiment_runner.start_date
time_shift = np.timedelta64(1, "h")
oifs_preprocessor = OIFSPreprocessor(start_date, time_shift)
nemo_preprocessor = NEMOPreprocessor(start_date, time_shift)

exp_id = "TOPS"
plot_folder = Path(f"plots/{exp_id}")
plot_folder.mkdir(exist_ok=True)
max_iters = experiment_runner.max_iters
alpha = 0.25

sequential_swr = False
if sequential_swr:
    step = 2
else:
    step = 1

oifs_diagvars = load_iterates(
    "diagvar.nc", oifs_preprocessor.preprocess, max_iters, step
)
oifs_progvars = load_iterates(
    "progvar.nc", oifs_preprocessor.preprocess, max_iters, step
)
nemo_t_grids = load_iterates(
    f"{exp_id}_*_T.nc", nemo_preprocessor.preprocess, max_iters, step
)
nemo_ice_grids = load_iterates(
    f"{exp_id}_*_icemod.nc", nemo_preprocessor.preprocess, max_iters, step
)


# %% 10m Temperature

axis_settings = {
    "title": "Temperature at 10m (OIFS)",
    "ylabel": "Temperature [°C]",
    "ylim": [-80, -35],
}

create_plots(oifs_progvars.t[:, :, 59] - 273.15, "10t_oifs", axis_settings)


# %% Surface Sensible Heat Flux
axis_settings = {
    "title": "Surface Sensible Heat Flux (OIFS)",
    "ylabel": "Heat Flux $[W m^{-2}]$",
    "ylim": [-1400, 200],
}

create_plots(oifs_diagvars.sfc_sen_flx, "ssh_oifs", axis_settings)

# %% SST

axis_settings = {
    "title": "Sea Surface Temperature (NEMO)",
    "ylabel": "Temperature [°C]",
    "ylim": [-2.1, -1.3],
}
create_plots(nemo_t_grids.sosstsst, "sst_nemo", axis_settings)

# %% SSW

axis_settings = {
    "title": "Surface SW Radiation (OIFS)",
    "ylabel": "Radiative Flux $[W m^{-2}]$",
    "ylim": [0, 80],
}

create_plots(oifs_diagvars.sfc_swrad, "ssw_oifs", axis_settings)

# %% Sea Ice Concentration


axis_settings = {
    "title": "Sea Ice Concentration (LIM3)",
    "ylabel": "Sea Ice Concentration [-]",
    "ylim": [0.99, 1],
}

create_plots(nemo_ice_grids.iceconc, "iceconc_lim3", axis_settings)

# %% Ice Surface Temperature

axis_settings = {
    "title": "Sea Ice Surface Temperature (LIM3)",
    "ylabel": "Temperature [°C]",
    "ylim": [-90, 5],
}

create_plots(nemo_ice_grids.icest, "icest_lim3", axis_settings)

# %% Mean Ice Temperature

axis_settings = {
    "title": "Mean Sea Ice Temperature (LIM3)",
    "ylabel": "Temperature [°C]",
    "ylim": [-10, -6],
}

create_plots(nemo_ice_grids.micet, "micet_lim3", axis_settings)

# %%

axis_settings = {
    "title": "Total Ice Heat Content (LIM3)",
    "ylabel": "Heat Content [J]",
    "ylim": [5.8e8, 6.25e8],
}

create_plots(nemo_ice_grids.icehc, "icehc_lim3", axis_settings)
# %%

for category in range(1, 6):
    axis_settings = {
        "title": f"Concentration of Thickness Category {category} (LIM3)",
        "ylabel": "Sea Ice Concentration [-]",
        "ylim": [0, 1],
    }

    create_plots(
        nemo_ice_grids.iceconc_cat.sel(ncatice=category),
        f"iceconc_cat{category}_lim3",
        axis_settings,
    )
# %%
