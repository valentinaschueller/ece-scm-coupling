"""
Convert Data from Copernicus Marine Environment Monitoring Service to suitable SI3 init file.
"""

from pathlib import Path
import pandas as pd
import xarray as xr

day_index = 0  # which daily average to extract (counts from 0!)
cmems_filename = Path("/home/x_valsc/aoscm/runtime/scm-classic/PAPA/data/nemo-4.0.1/init/cmems/cmems_top_case.nc")
template = Path("/home/x_valsc/rundir/templates/restart_si3_template.nc")

cmems_ds = xr.load_dataset(cmems_filename).isel(time=day_index)
cmems_ds = cmems_ds.sel(latitude=84, longitude=16)

extracted_date = pd.Timestamp(cmems_ds.time.data[()]).date()
new_si3_init_filename = template.parent / f"init_si3_{extracted_date}.nc"

si3_init_ds = xr.load_dataset(template)

si3_init_ds.a_i[:] = cmems_ds.siconc
si3_init_ds.v_i[:] = cmems_ds.sithick
si3_init_ds.t_su[:] = cmems_ds.thetao[0] + 273.15
si3_init_ds.nav_lat[:] = cmems_ds.latitude
si3_init_ds.nav_lon[:] = cmems_ds.longitude

si3_init_ds.to_netcdf(new_si3_init_filename)