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
    oce_cube = atm_cube[:, :, 9 * [0]]
    oce_cube.var_name = oce_var_name
    iris.save(oce_cube, oce_file_path)
