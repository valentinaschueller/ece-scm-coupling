from pathlib import Path

import pandas as pd
import xarray as xr

day_index = 0  # which daily average to extract from CMEMS data (counts from 0!)

cmems_filename = Path(
    "/home/x_valsc/aoscm/runtime/scm-classic/PAPA/data/nemo-4.0.1/init/cmems/cmems_top_case.nc"
)
old_rstos_filename = Path(
    "/home/x_valsc/aoscm/runtime/scm-classic/PAPA/data/oasis-mct-4.0/rstos.nc"
)

cmems_ds = xr.open_dataset(cmems_filename).isel(time=day_index, latitude=0, longitude=0)
rstos = xr.load_dataset(old_rstos_filename)

extracted_date = pd.Timestamp(cmems_ds.time.data[()]).date()
new_rstos_filename = old_rstos_filename.parent / f"rstos_{extracted_date}.nc"

cmems_sst = cmems_ds.thetao.isel(depth=0)
# convert to Kelvin
sst_for_rstos = cmems_sst.data + 273.15

rstos.O_SSTSST.data[:] = sst_for_rstos

if cmems_ds.sithick.isnull().data:
    rstos.OIceTck[:] = 0
else:
    rstos.OIceTck[:] = cmems_ds.sithick.data

if cmems_ds.siconc.isnull().data:
    rstos.OIceFrc[:] = 0
else:
    rstos.OIceFrc[:] = cmems_ds.siconc.data

# Snow thickness is not part of CMEMS output -> set it to 0 in all cases.
rstos.OSnwTck.data[:] = 0

rstos.to_netcdf(new_rstos_filename)
