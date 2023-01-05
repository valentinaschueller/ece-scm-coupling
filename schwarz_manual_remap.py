from pathlib import Path

import iris

import helpers as hlp
import remapping as rmp


class SchwarzCoupling:
    def __init__(
        self, exp_id: str, dt_cpl: int, dt_ifs: int, dt_nemo: int, cpl_scheme: int
    ):
        self.exp_id = exp_id
        self.dt_cpl = dt_cpl
        self.dt_ifs = dt_ifs
        self.dt_nemo = dt_nemo
        self.cpl_scheme = cpl_scheme
        self.initial_experiment = {}
        self.correction_experiment = {}
        self._generate_experiments()
        self.config_template = hlp.get_template("config-run.xml.j2")
        self.config_destination = Path("../aoscm/runtime/scm-classic/PAPA")
        self.max_iters = 5
        self.iter = 1
        self.run_directory = Path(f"PAPA/{self.exp_id}")

    def _generate_experiments(self):
        dct = {
            "exp_id": self.exp_id,
            "dt_cpl": self.dt_cpl,
            "dt_nemo": self.dt_nemo,
            "dt_ifs": self.dt_ifs,
            "cpl_scheme": self.cpl_scheme,
        }
        self.initial_experiment = dct
        dct = dct.copy()
        dct["script_name"] = "ece-scm_oifs+nemo_2"
        self.correction_experiment = dct

    def run(self):
        self._initial_guess()
        self._postprocess_initial_guess()
        self.iter += 1
        while self.iter <= self.max_iters:
            self._schwarz_correction()
            self._postprocess_correction()
            self.iter += 1

    def _initial_guess(self):
        print("Iteration 1")
        hlp.render_config_xml(
            self.config_destination, self.config_template, self.initial_experiment
        )
        hlp.run_model()

    def _schwarz_correction(self):
        print(f"Iteration {self.iter}")
        hlp.render_config_xml(
            self.config_destination, self.config_template, self.correction_experiment
        )
        hlp.run_model(executable=f"./{self.correction_experiment['script_name']}.sh")

    def _rename_run_directory(self):
        self.old_run_directory = self.run_directory.rename(
            self.run_directory.parent / f"{self.exp_id}_{self.iter}"
        )
        self.run_directory.mkdir()

    def _postprocess_initial_guess(self):
        print("Preparing iteration 2")

        self._rename_run_directory()

        # Create input files by discarding the first value of EXPOUT files and renaming appropriately
        for path in self.old_run_directory.glob("*.nc"):
            if "_ATMIFS_" in path.stem:
                atm_var_name = path.stem.split("_ATMIFS_")[0]
                oce_var_name = rmp.atm_to_oce.get(atm_var_name, None)
                if oce_var_name is None:
                    continue
                oce_file_path_tmp = self.run_directory / f"{oce_var_name}_tmp.nc"
                oce_file_path = self.run_directory / f"{oce_var_name}.nc"
                rmp.remap_atm_to_oce(
                    str(path), atm_var_name, oce_file_path_tmp, oce_var_name
                )
                oce_var = iris.load_cube(str(oce_file_path_tmp), oce_var_name)
                if self.cpl_scheme != 1:
                    oce_var = oce_var[1:]
                oce_var.coord("time").points = oce_var.coord("time").points - (
                    dt_cpl - dt_ifs
                )
                iris.save(oce_var, oce_file_path)
                oce_file_path_tmp.unlink()
            if "_oceanx_" in path.stem:
                oce_var_name = path.stem.split("_oceanx_")[0]
                atm_var_name = rmp.oce_to_atm.get(oce_var_name, None)
                if atm_var_name is None:
                    continue
                atm_file_path_tmp = self.run_directory / f"{atm_var_name}_tmp.nc"
                atm_file_path = self.run_directory / f"{atm_var_name}.nc"
                rmp.remap_oce_to_atm(
                    str(path), oce_var_name, atm_file_path_tmp, atm_var_name
                )
                atm_var = iris.load_cube(str(atm_file_path_tmp), atm_var_name)
                if self.cpl_scheme != 2:
                    atm_var = atm_var[1:]
                atm_var.coord("time").points = atm_var.coord("time").points - (
                    dt_cpl - dt_nemo
                )
                iris.save(atm_var, atm_file_path)
                atm_file_path_tmp.unlink()

        print("Renamed EXPOUT files generated by OASIS")

    def _postprocess_correction(self) -> None:
        print(f"Preparing iteration {self.iter + 1}")
        self._rename_run_directory()
        print("Run directory copied")
        for path in self.old_run_directory.glob("*.nc"):
            if "_ATMIFS_" in path.stem:
                atm_var_name = path.stem.split("_ATMIFS_")[0]
                oce_var_name = rmp.atm_to_oce[atm_var_name]
                oce_file_path = self.run_directory / f"{oce_var_name}.nc"
                rmp.remap_atm_to_oce(
                    str(path), atm_var_name, oce_file_path, oce_var_name
                )
            if "_oceanx_" in path.stem:
                oce_var_name = path.stem.split("_oceanx_")[0]
                atm_var_name = rmp.oce_to_atm[oce_var_name]
                atm_file_path = self.run_directory / f"{atm_var_name}.nc"
                rmp.remap_oce_to_atm(
                    str(path), oce_var_name, atm_file_path, atm_var_name
                )
        print("Remapped OUTPUT files generated by OASIS")


exp_id = "SWZB"
dt_cpl = 7200
dt_ifs = 900
dt_nemo = 1800
cpl_scheme = 2

swz8 = SchwarzCoupling(exp_id, dt_cpl, dt_ifs, dt_nemo, cpl_scheme)

swz8.run()
