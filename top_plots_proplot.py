# %%
from pathlib import Path

import numpy as np
import proplot as pplt
import xarray as xr

import top_case as experiment_runner
from utils.files import NEMOPreprocessor, OIFSPreprocessor
from utils.plotting import load_from_multiple_experiments

# %%

base_exp_id = experiment_runner.exp_prefix
plotting_output_directory = Path(f"plots/TOP_case/{base_exp_id}")
plotting_output_directory.mkdir(exist_ok=True)

start_date = experiment_runner.start_date
time_shift = np.timedelta64(1, "h")
oifs_preprocessor = OIFSPreprocessor(start_date, time_shift)
nemo_preprocessor = NEMOPreprocessor(start_date, time_shift)

# %%
max_iters = experiment_runner.max_iters

# %%
experiments = [
    f"{base_exp_id}0",
    f"{base_exp_id}1",
    f"{base_exp_id}2",
    f"{base_exp_id}S_{max_iters}",
]
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
titles = [
    "Parallel",
    "Sequential Atmosphere-First",
    "Sequential Ocean-First",
    "SWR (k=50)",
]

# %% Vertical Temperature Profile

oifs_progvar_p = oifs_progvar.assign_coords(
    air_pressure=("nlev", oifs_progvar.pressure_f[0, 0].data / 100)
)
oifs_progvar_p = oifs_progvar_p.swap_dims({"nlev": "air_pressure"})

fig, axs = pplt.subplots(nrows=4, ncols=1, width="70em", height="90em")
axs.format(suptitle="Vertical Atmospheric Humidity Profiles in BL (TOP Case)")

for i in range(len(titles)):
    ax = axs[i]
    im = ax.contourf(
        oifs_progvar_p.t[i, :, 100:] - 273.15,
        levels=14,
        transpose=True,
        discrete=True,
        vmin=-36,
        vmax=-15,
    )
    ax.set_ylabel("Air Pressure [hPa]")
    ax.invert_yaxis()
    ax.set_title(titles[i])
    ax.format(xrotation=30)
fig.colorbar(im, loc="b", title="Temperature [°C]")
fig.savefig(plotting_output_directory / "oifs_t_profile.pdf")

# %% Vertical Humidity Profile

fig, axs = pplt.subplots(nrows=4, ncols=1, width="70em", height="90em")
axs.format(suptitle="Vertical Atmospheric Humidity Profiles in BL (TOP Case)")

for i in range(len(titles)):
    ax = axs[i]
    im = ax.contourf(
        oifs_progvar_p.q[i, :, 100:] * 1e3,
        levels=12,
        transpose=True,
        discrete=True,
        vmin=0.1,
        vmax=0.8,
    )
    ax.set_ylabel("Air Pressure [hPa]")
    ax.invert_yaxis()
    ax.set_title(titles[i])
    ax.format(xrotation=30)
fig.colorbar(im, loc="b", title="Water Vapor Mixing Ratio [g/kg]")
fig.savefig(plotting_output_directory / "oifs_q_profile.pdf")


# %% Ocean Vertical Temperature Profile

fig, axs = pplt.subplots(nrows=4, ncols=1, width="70em", height="90em")
axs.format(suptitle="Vertical Ocean Temperature Profiles in Mixed Layer (TOP Case)")

for i in range(len(titles)):
    ax = axs[i]
    im = ax.contourf(
        nemo_t_grid.votemper[i, :, :10],
        levels=14,
        discrete=True,
        transpose=True,
        vmin=-2.0,
        vmax=-1.0,
    )
    ax.invert_yaxis()
    ax.format(title=titles[i], xlabel="Time", ylabel="Depth [m]", xrotation=30)
fig.colorbar(im, loc="b", title="Temperature [°C]")
fig.savefig(plotting_output_directory / "nemo_t_profiles.pdf")

# %%  OIFS Prognostic Variables on Lowest Model Level

colors = ["m", "c", "y", "k"]
labels = ["parallel", "atmosphere-first", "ocean-first", "SWR (k=50)"]
alpha = 1
linestyles = ["--", ":", "-.", "-"]

fig, axs = pplt.subplots(nrows=4, spany=False, height="45em", width="75em")

ax = axs[0]
for i in range(len(colors)):
    ax.plot(
        oifs_progvar.u.isel(nlev=-1, cpl_scheme=i),
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )
ax.format(
    ylabel="Zonal Wind \n$[m\; s^{{-1}}]$",
    title="",
    xlabel="Time",
    # ylim=[-10, 10],
)

ax = axs[1]
for i in range(len(colors)):
    ax.plot(
        oifs_progvar.v.isel(nlev=-1, cpl_scheme=i),
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )
ax.format(
    ylabel=f"Meridional Wind \n$[m\; s^{{-1}}]$",
    title="",
    xlabel="Time",
    # ylim=[-10, 10],
)

ax = axs[2]
for i in range(len(colors)):
    ax.plot(
        oifs_progvar.t.isel(nlev=-1, cpl_scheme=i) - 273.15,
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )
ax.format(ylabel="Temperature \n$[°C]$", title="", xlabel="Time")

hs = []
ax = axs[3]
for i in range(len(colors)):
    linestyle = linestyles[i]
    h = ax.plot(
        oifs_progvar.q.isel(nlev=-1, cpl_scheme=i) * 1e3,
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )
    hs.append(h)
ax.format(
    ylabel="Humidity $[g\; kg^{{-1}}]$",
    title="",
    xlabel="Time",
    # ylim=[5, 10],
    xrotation=30,
)

# axs.format(suptitle="OpenIFS Prognostic Variables on Lowest Model Level")

fig.legend(hs, ncols=4, frame=False, loc="b")
fig.savefig(plotting_output_directory / "oifs_progvars.pdf")

# %% Temperature: Study Tendencies

colors = ["m", "c", "y", "k"]
labels = ["parallel", "atm-first", "oce-first", "SWR (k=50)"]
alpha = 1
linestyles = ["--", ":", "-.", "-"]

fig, axs = pplt.subplots(nrows=3, spany=False, height="50em", width="70em")
axs.format(suptitle="Temperature Tendency Split in TOP Case")

ax = axs[0]
for i in range(len(colors)):
    ax.plot(
        oifs_diagvar.tend_temp.isel(nlev=-1, cpl_scheme=i),
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )
ax.format(
    ylabel=r"$\partial_t T$ $[K\; s^{-1}]$",
    title="",
    xlabel="Time",
    # ylim=[-25e-5, 25e-5],
)

ax = axs[1]
hs = []
for i in range(len(colors)):
    h = ax.plot(
        oifs_diagvar.tend_temp_d.isel(nlev=-1, cpl_scheme=i),
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )
    hs.append(h)
ax.format(
    ylabel=r"$(\partial_t T)_\mathrm{dyn}$ $[K\; s^{-1}]$",
    title="",
    xlabel="Time",
    # ylim=[-25e-5, 25e-5],
)

ax = axs[2]
for i in range(len(colors)):
    ax.plot(
        oifs_diagvar.tend_temp_p.isel(nlev=-1, cpl_scheme=i),
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )
ax.format(
    ylabel=r"$(\partial_t T)_\mathrm{phy}$ $[K\; s^{-1}]$",
    title="",
    xlabel="Time",
    xrotation=30,
    # ylim=[-25e-5, 25e-5],
)

axs.format(yformatter="sci")
fig.legend(hs, frame=False, ncols=4, loc="b")
fig.savefig(plotting_output_directory / "oifs_t_tendency_split.pdf")

# %% Humidity Tendencies

colors = ["m", "c", "y", "k"]
labels = ["parallel", "atm-first", "oce-first", "SWR (k=50)"]
alpha = 1
linestyles = ["--", ":", "-.", "-"]

fig, axs = pplt.subplots(nrows=3, spany=False, height="50em", width="70em")
axs.format(suptitle="Humidity Tendency Split in TOP Case")

ax = axs[0]
for i in range(len(colors)):
    ax.plot(
        oifs_diagvar.tend_wat_vap.isel(nlev=-1, cpl_scheme=i),
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )
ax.format(ylabel=r"$\partial_t q$ $[s^{-1}]$", title="", xlabel="Time")

ax = axs[1]
hs = []
for i in range(len(colors)):
    h = ax.plot(
        oifs_diagvar.tend_wat_vap_d.isel(nlev=-1, cpl_scheme=i),
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )
    hs.append(h)
ax.format(ylabel=r"$(\partial_t q)_\mathrm{dyn}$ $[s^{-1}]$", title="", xlabel="Time")

ax = axs[2]
for i in range(len(colors)):
    ax.plot(
        oifs_diagvar.tend_wat_vap_p.isel(nlev=-1, cpl_scheme=i),
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )
ax.format(ylabel=r"$(\partial_t q)_\mathrm{phy}$ $[s^{-1}]$", title="", xlabel="Time")

axs.format(yformatter="sci")
fig.legend(hs, frame=False, ncols=4, loc="b")
fig.savefig(plotting_output_directory / "oifs_q_tendency_split.pdf")

# %% Ocean Prognostic Variables

colors = ["m", "c", "y", "k"]
labels = ["parallel", "atmosphere-first", "ocean-first", "SWR (k=50)"]
alpha = 1
linestyles = ["--", ":", "-.", "-"]

fig, axs = pplt.subplots(nrows=4, spany=False, height="45em", width="75em")

ax = axs[0]
for i in range(len(colors)):
    ax.plot(
        nemo_u_grid.vozocrtx.isel(depthu=0, cpl_scheme=i),
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )
ax.format(
    ylabel=f"Zonal Current \n $[m\; s^{{-1}}]$",
    title="",
    xlabel="Time",
    # ylim=[-0.15, 0.15],
)

ax = axs[1]
for i in range(len(colors)):
    ax.plot(
        nemo_v_grid.vomecrty.isel(depthv=0, cpl_scheme=i),
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )
ax.format(
    ylabel=f"Meridional Current \n $[m\; s^{{-1}}]$",
    title="",
    xlabel="Time",
    # ylim=[-0.15, 0.15],
)

ax = axs[2]
for i in range(len(colors)):
    ax.plot(
        nemo_t_grid.sosstsst.isel(cpl_scheme=i),
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )
ax.format(ylabel=f"Temperature \n$[°C]$", title="", xlabel="Time")

hs = []
ax = axs[3]
for i in range(len(colors)):
    h = ax.plot(
        nemo_t_grid.vosaline.isel(deptht=0, cpl_scheme=i),
        color=colors[i],
        label=labels[i],
        ls=linestyles[i],
    )
    hs.append(h)
ax.format(ylabel="Salinity [PSU]", title="", xlabel="Time")

axs.format(xrotation=30)
# axs.format(suptitle="NEMO Prognostic Variables at the Surface", )

fig.legend(hs, ncols=4, frame=False, loc="b")
fig.savefig(plotting_output_directory / "nemo_progvars.pdf")

# %%
