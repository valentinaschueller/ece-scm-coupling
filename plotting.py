import iris
import xarray as xr


def create_atm_temps_plot(ax_atm_temp, atm_temps, colors, alpha, labels, linestyles):
    assert len(colors) == len(atm_temps)
    for i in range(len(colors)):
        atm_temp = atm_temps[i]
        color = colors[i]
        label = labels[i]
        linestyle = linestyles[i]
        atm_temp.convert_units("degC")
        time_coord = atm_temp.coord("time")
        new_time_coord = iris.coords.DimCoord(
            time_coord.points,
            standard_name="time",
            long_name="Time",
            var_name="time",
            units="seconds since 2014-07-01 00:00:00",
        )
        # time shift: -7h from UTC to PDT
        new_time_coord.points = new_time_coord.points - 7 * 3600
        atm_temp.remove_coord("time")
        atm_temp.add_dim_coord(new_time_coord, 0)
        da = xr.DataArray.from_iris(atm_temp[:, 59])
        ax_atm_temp.plot(
            da,
            color=color,
            label=label,
            alpha=alpha,
            ls=linestyle,
        )
    ax_atm_temp.set_ybound(8, 14)
    ax_atm_temp.set_ylabel("T10m [°C]")
    ax_atm_temp.set_yticks(list(range(8, 15)))
    ax_atm_temp.set_title("")
    ax_atm_temp.legend(ncols=1)


def create_oce_ssts_plot(ax_oce_sst, oce_ssts, colors, alpha, labels, linestyles):
    assert len(colors) == len(oce_ssts)
    for i in range(len(colors)):
        oce_sst = oce_ssts[i]
        color = colors[i]
        label = labels[i]
        linestyle = linestyles[i]
        time_coord = oce_sst.coord("time")
        # time shift: -7h from UTC to PDT
        time_coord.points = time_coord.points - 7 * 3600
        time_coord.bounds = time_coord.bounds - 7 * 3600
        da = xr.DataArray.from_iris(oce_sst[:, 1, 1])
        ax_oce_sst.plot(
            da,
            color=color,
            label=label,
            alpha=alpha,
            ls=linestyle,
        )
    ax_oce_sst.set_ybound(8, 14)
    ax_oce_sst.set_ylabel("SST [°C]")
    ax_oce_sst.set_yticks(list(range(8, 15)))
    ax_oce_sst.set_title("")


def create_atm_ssws_plot(ax_atm_ssw, atm_ssws, colors, alpha, labels, linestyles):
    assert len(colors) == len(atm_ssws)
    for i in range(len(colors)):
        atm_ssw = atm_ssws[i]
        color = colors[i]
        label = labels[i]
        linestyle = linestyles[i]
        time_coord = atm_ssw.coord("time")
        new_time_coord = iris.coords.DimCoord(
            time_coord.points,
            standard_name="time",
            long_name="Time",
            var_name="time",
            units="seconds since 2014-07-01 00:00:00",
        )
        # time shift: -7h from UTC to PDT
        new_time_coord.points = new_time_coord.points - 7 * 3600
        atm_ssw.remove_coord("time")
        atm_ssw.add_dim_coord(new_time_coord, 0)
        da = xr.DataArray.from_iris(atm_ssw)
        ax_atm_ssw.plot(
            da,
            color=color,
            label=label,
            alpha=alpha,
            ls=linestyle,
        )
    ax_atm_ssw.set_title("")
    ax_atm_ssw.set_ylabel(r"Atm sfc radiation [$W m^{-2}$]")
    ax_atm_ssw.set_ybound(0, 1000)


def create_oce_ssws_plot(ax_oce_ssw, oce_ssws, colors, alpha, labels, linestyles):
    assert len(colors) == len(oce_ssws)
    for i in range(len(colors)):
        oce_ssw = oce_ssws[i]
        time_coord = oce_ssw.coord("time")
        # time shift: -7h from UTC to PDT
        time_coord.points = time_coord.points - 7 * 3600
        time_coord.bounds = time_coord.bounds - 7 * 3600
        color = colors[i]
        label = labels[i]
        linestyle = linestyles[i]
        da = xr.DataArray.from_iris(oce_ssw[:, 1, 1])
        ax_oce_ssw.plot(
            da,
            color=color,
            label=label,
            alpha=alpha,
            ls=linestyle,
        )
    ax_oce_ssw.set_title("")
    ax_oce_ssw.set_xlabel("")
    ax_oce_ssw.set_ylabel(r"Oce sfc radiation [$W m^{-2}$]")
    ax_oce_ssw.set_ybound(0, 800)
