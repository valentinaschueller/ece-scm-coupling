# %% Setup
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

import top_case as experiment_runner
from utils.files import NEMOPreprocessor, OIFSPreprocessor
from utils.plotting import load_from_multiple_experiments

plt.style.use("stylesheet.mpl")

start_date = experiment_runner.start_date
time_shift = np.timedelta64(1, "h")
oifs_preprocessor = OIFSPreprocessor(start_date, time_shift)
nemo_preprocessor = NEMOPreprocessor(start_date, time_shift)


base_exp_id = experiment_runner.exp_prefix
max_schwarz_iters = experiment_runner.max_iters
schwarz_exp_id = f"{base_exp_id}S"
experiments = [
    f"{base_exp_id}0",
    f"{base_exp_id}1",
    f"{base_exp_id}2",
    f"{schwarz_exp_id}_{max_schwarz_iters}",
]

plotting_output_directory = Path(f"plots/TOP_case/{base_exp_id}")
plotting_output_directory.mkdir(exist_ok=True)

swr_plot_folder = Path(f"plots/{schwarz_exp_id}")
swr_plot_folder.mkdir(exist_ok=True)


max_iters = experiment_runner.max_iters
alpha = 0.25

sequential_swr = False
if sequential_swr:
    step = 2
else:
    step = 1


def load_iterates(
    file_name: str, preprocess: callable, max_iters: int, step: int
) -> xr.Dataset:
    directories = [f"{schwarz_exp_id}_{iter}" for iter in range(1, max_iters + 1, step)]
    swr_dim = xr.DataArray(np.arange(max_iters) + 1, dims="swr_iterate")
    return load_from_multiple_experiments(file_name, directories, preprocess, swr_dim)


nemo_ice_grid_swr = load_iterates(
    f"*_icemod.nc", nemo_preprocessor.preprocess, max_iters, step
)
iceconc_cat_diff = nemo_ice_grid_swr.iceconc_cat - nemo_ice_grid_swr.iceconc_cat.isel(
    swr_iterate=0
)


# %%

fig, ax = plt.subplots()
fig.set(figwidth=8, figheight=5)
ax.set(
    xlabel="SWR Iterate $i$",
    ylabel=r"$\Delta$ Ice Concentration",
    title=r"Change in Concentration by Category $l$: $\max_{t_n} |\mathrm{conc}_{l,i} - \mathrm{conc}_{l,1}|$",
    xlim=[1, max_iters],
)
max_abs_diff = abs(iceconc_cat_diff).max(dim="time")
for category in range(1, 6):
    ax.plot(
        iceconc_cat_diff.swr_iterate + 1,
        max_abs_diff.sel(ncatice=category),
        label=f"Category {category}",
    )
ax.legend()
fig.savefig(swr_plot_folder / "siconc_change_category.pdf", bbox_inches="tight")
# %% Accumulate Difference across Categories, then take difference

fig, ax = plt.subplots()
fig.set(figwidth=8, figheight=5)
ax.set(
    xlabel="SWR Iterate $i$",
    ylabel=r"$\Delta$ Ice Concentration",
    title=r"Biggest Shift between Categories $l$: $\max_{t_n} \sum_{l=1}^{5}|\mathrm{conc}_{l,i} - \mathrm{conc}_{l,1}|$",
    xlim=[1, max_iters],
)
sum_abs_diff = abs(iceconc_cat_diff).sum(dim="ncatice")
max_total_change = sum_abs_diff.max(dim="time")
ax.plot(max_total_change.swr_iterate + 1, max_total_change, color="k")
fig.savefig(swr_plot_folder / "siconc_biggest_total_shift.pdf", bbox_inches="tight")

# %% Compare coupling

cpl_dim = xr.DataArray(["par", "atm", "oce", "swr"], dims="cpl_scheme")
oifs_progvar = load_from_multiple_experiments(
    "progvar.nc", experiments, oifs_preprocessor.preprocess, cpl_dim
)
oifs_diagvar = load_from_multiple_experiments(
    "diagvar.nc", experiments, oifs_preprocessor.preprocess, cpl_dim
)
nemo_t_grid = load_from_multiple_experiments(
    "*_T.nc", experiments, nemo_preprocessor.preprocess, cpl_dim
)
nemo_u_grid = load_from_multiple_experiments(
    "*_U.nc", experiments, nemo_preprocessor.preprocess, cpl_dim
)
nemo_v_grid = load_from_multiple_experiments(
    "*_V.nc", experiments, nemo_preprocessor.preprocess, cpl_dim
)
nemo_ice_grid = load_from_multiple_experiments(
    "*_icemod.nc", experiments, nemo_preprocessor.preprocess, cpl_dim
)

# %%

colors = ["m", "c", "y", "k"]
labels = ["parallel", "atm-first", "oce-first", f"SWR (k={max_iters})"]
linestyles = ["--", ":", "-.", "-"]

# %% OIFS PBL Height

fig, ax = plt.subplots()

fig.set(figwidth=7, figheight=5)
for i in range(len(colors)):
    ax.plot(
        oifs_diagvar.time,
        oifs_diagvar.pbl_height[i],
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )

ax.set(
    ylabel=r"Boundary Layer Height $[m]$",
    xlabel="Time",
    title="Boundary Layer Height (TOP Case)",
)
ax.grid(True)
ax.legend()
ax.xaxis.set_tick_params(rotation=30)
fig.savefig(plotting_output_directory / "oifs_pbl_height.pdf")
# %% NEMO Mixed Layer Depth

# According to this report, p. 18: https://www.drakkar-ocean.eu/publications/reports/orca025-grd100-report-dussin, the first 10 levels should suffice for NEMO as well.

fig, ax = plt.subplots()

fig.set(figwidth=7, figheight=5)
for i in range(len(colors)):
    ax.plot(
        nemo_t_grid.time,
        nemo_t_grid.somxl010[i],
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )

ax.set(
    ylabel="Mixed Layer Depth [m]",
    xlabel="Time",
    title="Mixed Layer Depth (TOP Case)",
    ylim=[0, 50],
)
ax.grid(True)
ax.legend()
ax.xaxis.set_tick_params(rotation=30)
fig.savefig(plotting_output_directory / "nemo_mldepth.pdf")


# %% OIFS Cloud Cover

fig, ax = plt.subplots()

fig.set(figwidth=7, figheight=5)
for i in range(len(colors)):
    ax.plot(
        oifs_diagvar.time,
        oifs_diagvar.total_cloud[i],
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )

ax.set(
    title="Total Cloud Cover (TOP Case)",
    xlabel="Time",
    ylabel="Cloud Cover",
    xmargin=0.0,
)
ax.grid(True)
ax.legend()
ax.xaxis.set_tick_params(rotation=30)
fig.savefig(plotting_output_directory / "oifs_ccover.pdf")


# %% Surface Heat Fluxes

plt.style.use("stylesheet.mpl")

colors = ["m", "c", "y", "k"]
labels = ["parallel", "atmosphere-first", "ocean-first", "SWR (k=50)"]
linestyles = ["--", ":", "-.", "-"]

fig, axs = plt.subplots(nrows=2, ncols=2, sharex=True)
fig.set(
    figwidth=12,
    figheight=8,
)

ax = axs[0, 0]
for i in range(len(colors)):
    ax.plot(
        oifs_diagvar.time,
        oifs_diagvar.sfc_sen_flx[i],
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )
ax.set(
    ylabel=r"Heat Flux $[W \; m^{-2}]$",
    title="Surface Sensible Heat Flux",
    ylim=[-300, 300],
)

ax = axs[0, 1]
for i in range(len(colors)):
    ax.plot(
        oifs_diagvar.time,
        oifs_diagvar.sfc_lat_flx[i],
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )
ax.set(title="Surface Latent Heat Flux", ylim=[-300, 300])

ax = axs[1, 0]
for i in range(len(colors)):
    ax.plot(
        oifs_diagvar.time,
        oifs_diagvar.sfc_swrad[i],
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )
ax.set(
    ylabel=r"Radiation $[W \; m^{-2}]$",
    ylim=[-100, 100],
    title="Net Surface Shortwave Radiation",
)
ax.xaxis.set_tick_params(rotation=30)

ax = axs[1, 1]
for i in range(len(colors)):
    ax.plot(
        oifs_diagvar.time,
        oifs_diagvar.sfc_lwrad[i],
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )
ax.set(
    title="Net Surface Longwave Radiation",
    ylim=[-100, 100],
)
ax.xaxis.set_tick_params(rotation=30)

fig.supxlabel("Time")
fig.legend(
    labels, ncol=4, loc="center", bbox_to_anchor=(0.0, -0.12, 1.0, 0.2), frameon=False
)

fig.savefig(plotting_output_directory / "surface_heat_fluxes.pdf")
