"""
Convert Data from Copernicus Marine Environment Monitoring Service to suitable NEMO init file.
"""

import pandas as pd
import xarray as xr

day_index = 0  # which daily average to extract (counts from 0!)
cmems_filename = "/home/x_valsc/rundir/data/cmems_papa_with_seaice.nc"
old_nemo_init_filename = (
    "aoscm/runtime/scm-classic/PAPA/data/nemo-4.0.1/init/init_PAPASTATION_m06d15.nc"
)

cmems_ds = xr.load_dataset(cmems_filename).isel(time=day_index)
cmems_temperature = cmems_ds.thetao
cmems_zonal_current = cmems_ds.uo
cmems_meridional_current = cmems_ds.vo
cmems_salinity = cmems_ds.so

extracted_date = pd.Timestamp(cmems_ds.time.data[()]).date()
new_nemo_init_filename = f"init_PAPASTATION_{extracted_date}.nc"

nemo_init_ds = xr.load_dataset(old_nemo_init_filename)
nemo_init_temperature = nemo_init_ds.votemper[0]
nemo_init_salinity = nemo_init_ds.vosaline[0]
try:
    use_currents = True
    nemo_init_zonal_current = nemo_init_ds.vozocrtx[0]
    nemo_init_meridional_current = nemo_init_ds.vomecrty[0]
except AttributeError:
    use_currents = False
    nemo_init_zonal_current = None
    nemo_init_meridional_current = None

cmems_temperature = cmems_temperature.interp(depth=nemo_init_ds.deptht.data)
cmems_salinity = cmems_salinity.interp(depth=nemo_init_ds.deptht.data)
if use_currents:
    cmems_meridional_current = cmems_meridional_current.interp(
        depth=nemo_init_ds.depthu.data
    )
    cmems_zonal_current = cmems_zonal_current.interp(depth=nemo_init_ds.depthv.data)


def extrapolate_with_constant_values(cmems_output: xr.DataArray) -> xr.DataArray:
    # using https://stackoverflow.com/a/49759690/11247528
    last_not_null_index = (~cmems_output.isnull()).cumsum("depth").argmax("depth")
    sea_floor_value = cmems_output[last_not_null_index]
    return cmems_output.fillna(sea_floor_value)


cmems_temperature = extrapolate_with_constant_values(cmems_temperature)
cmems_salinity = extrapolate_with_constant_values(cmems_salinity)
cmems_meridional_current = extrapolate_with_constant_values(cmems_meridional_current)
cmems_zonal_current = extrapolate_with_constant_values(cmems_zonal_current)

nemo_init_temperature.data[:, :] = cmems_temperature.data
nemo_init_salinity.data[:, :] = cmems_salinity.data
if use_currents:
    nemo_init_zonal_current.data[:, :] = cmems_zonal_current.data
    nemo_init_meridional_current.data[:, :] = cmems_meridional_current.data

nemo_init_ds.to_netcdf(new_nemo_init_filename)
