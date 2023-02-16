from pathlib import Path

import user_context as context
import utils.helpers as hlp
from remapping import RemapCouplerOutput
from utils.templates import render_config_xml


class SchwarzCoupling:
    def __init__(self, experiment_dict: dict):
        self.input_dict = experiment_dict
        self.exp_id = experiment_dict["exp_id"]
        self.dt_cpl = experiment_dict["dt_cpl"]
        self.dt_ifs = experiment_dict["dt_ifs"]
        self.dt_nemo = experiment_dict["dt_nemo"]
        self.cpl_scheme = experiment_dict["cpl_scheme"]
        self.initial_experiment = {}
        self.correction_experiment = {}
        self._generate_experiments()
        self.iter = 1
        self.run_directory = Path(f"PAPA/{self.exp_id}")

    def _generate_experiments(self):
        self.initial_experiment = self.input_dict.copy()
        dct = self.input_dict.copy()
        dct["script_name"] = "ece-scm_oifs+nemo_2"
        self.correction_experiment = dct

    def run(self, max_iters: int, current_iter: int = 1):
        if max_iters < 1:
            raise ValueError("Maximum amount of iterations must be >= 1")
        if current_iter < 1:
            raise ValueError("Current iteration must be >=1")
        self.iter = current_iter
        if self.iter == 1:
            self._initial_guess()
            self._rename_run_directory()
        while self.iter < max_iters:
            self.iter += 1
            self._prepare_iteration()
            self._schwarz_correction()
            self._rename_run_directory()
        self.run_directory.rmdir()

    def _initial_guess(self):
        print("Iteration 1")
        render_config_xml(
            context.runscript_dir, context.config_run_template, self.initial_experiment
        )
        hlp.run_model()

    def _schwarz_correction(self):
        print(f"Iteration {self.iter}")
        render_config_xml(
            context.runscript_dir,
            context.config_run_template,
            self.correction_experiment,
        )
        hlp.run_model(executable=f"./{self.correction_experiment['script_name']}.sh")
        # hlp.clean_model_output(self.run_directory)

    def _rename_run_directory(self):
        self.run_directory.rename(
            self.run_directory.parent / f"{self.exp_id}_{self.iter}"
        )
        self.run_directory.mkdir()

    def _prepare_iteration(self):
        print(f"Preparing iteration {self.iter}")

        old_run_directory = self.run_directory.parent / f"{self.exp_id}_{self.iter - 1}"

        remapper = RemapCouplerOutput(
            old_run_directory,
            self.run_directory,
            self.cpl_scheme,
            self.dt_cpl,
            self.dt_ifs,
            self.dt_nemo,
        )
        remapper.remap()

        print("Remapped files generated by OASIS.")
