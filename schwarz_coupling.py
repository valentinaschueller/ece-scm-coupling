import user_context as context
from remapping import RemapCouplerOutput
from utils.helpers import AOSCM, reduce_output, serialize_experiment_setup
from utils.templates import render_config_xml


class SchwarzCoupling:
    def __init__(self, experiment_dict: dict):
        self.exp_id = experiment_dict["exp_id"]
        self.dt_cpl = experiment_dict["dt_cpl"]
        self.dt_ifs = experiment_dict["dt_ifs"]
        self.dt_nemo = experiment_dict["dt_nemo"]
        self.cpl_scheme = experiment_dict["cpl_scheme"]
        self.experiment = experiment_dict
        self.iter = 1
        self.run_directory = context.output_dir / self.exp_id
        self.aoscm = AOSCM(
            context.runscript_dir,
            context.ecconf_executable,
            context.platform,
        )

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
            context.runscript_dir, context.config_run_template, self.experiment
        )
        self.aoscm.run_coupled_model(schwarz_correction=False)

    def _schwarz_correction(self):
        print(f"Iteration {self.iter}")
        render_config_xml(
            context.runscript_dir,
            context.config_run_template,
            self.experiment,
        )
        self.aoscm.run_coupled_model(schwarz_correction=True)

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

        reduce_output(old_run_directory, keep_debug_output=False)
        serialize_experiment_setup(self.experiment, old_run_directory)
