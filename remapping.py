from pathlib import Path

import iris


def remap_oce_to_atm(
    oce_file_path: str, oce_var_name: str, atm_file_path: Path, atm_var_name: str
):
    oce_cube = iris.load_cube(oce_file_path, oce_var_name)
    atm_cube = oce_cube[:, :, [4]]
    atm_cube.var_name = atm_var_name
    iris.save(atm_cube, atm_file_path)


def remap_atm_to_oce(
    atm_file_path: str, atm_var_name: str, oce_file_path: Path, oce_var_name: str
):
    atm_cube = iris.load_cube(atm_file_path, atm_var_name)
    tmp_cube = atm_cube[:, :, 3 * [0]]
    oce_cube = tmp_cube[:, 3 * [0], :]
    oce_cube.var_name = oce_var_name
    iris.save(oce_cube, oce_file_path)


atm_to_oce = {
    "A_TauX_oce": "O_OTaux1",
    "A_TauY_oce": "O_OTauy1",
    "A_TauX_ice": "O_ITaux1",
    "A_TauY_ice": "O_ITauy1",
    "A_Qs_mix": "O_QsrMix",
    "A_Qns_mix": "O_QnsMix",
    "A_Qs_ice": "O_QsrIce",
    "A_Qns_ice": "O_QnsIce",
    "A_Precip_liquid": "OTotRain",
    "A_Precip_solid": "OTotSnow",
    "A_Evap_total": "OTotEvap",
    "A_Evap_ice": "OIceEvap",
    "A_dQns_dT": "O_dQnsdT",
}

oce_to_atm = {
    "O_SSTSST": "A_SST",
    "O_TepIce": "A_Ice_temp",
    "O_AlbIce": "A_Ice_albedo",
    "OIceFrc": "A_Ice_frac",
    "OIceTck": "A_Ice_thickness",
    "OSnwTck": "A_Snow_thickness",
}
