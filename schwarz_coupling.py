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
        while self.iter <= max_iters:
            print(f"Iteration {self.iter}")
            render_config_xml(
                context.runscript_dir, context.config_run_template, self.experiment
            )
            self.aoscm.run_coupled_model(schwarz_correction=bool(self.iter - 1))
            self._postprocess_iteration(next_iteration_exists=(self.iter < max_iters))
            self.iter += 1

    def _postprocess_iteration(self, next_iteration_exists: bool):
        print(f"Postprocessing iteration {self.iter}")

        renamed_directory = self.run_directory.parent / f"{self.exp_id}_{self.iter}"
        self.run_directory.rename(renamed_directory)

        if next_iteration_exists:
            self.run_directory.mkdir()
            remapper = RemapCouplerOutput(
                renamed_directory,
                self.run_directory,
                self.cpl_scheme,
                self.dt_cpl,
                self.dt_ifs,
                self.dt_nemo,
            )
            remapper.remap()

        reduce_output(renamed_directory, keep_debug_output=False)
        serialize_experiment_setup(self.experiment, renamed_directory)
