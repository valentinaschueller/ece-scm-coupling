import shutil

from AOSCMcoupling.context import Context
from AOSCMcoupling.convergence_checker import ConvergenceChecker
from AOSCMcoupling.experiment import Experiment
from AOSCMcoupling.helpers import AOSCM, reduce_output, serialize_experiment_setup
from AOSCMcoupling.remapping import RemapCouplerOutput
from AOSCMcoupling.templates import render_config_xml


class SchwarzCoupling:
    """Wrapper class to run AOSCM experiments with Schwarz WR."""

    def __init__(
        self,
        experiment: Experiment,
        context: Context,
        reduce_output_after_iteration: bool = True,
    ):
        self.context = context
        self.exp_id = experiment.exp_id
        self.experiment = experiment
        self.iter = 1
        self.run_directory = context.output_dir / self.exp_id
        self.aoscm = AOSCM(context)
        self.convergence_checker = ConvergenceChecker()
        self.reduce_output = reduce_output_after_iteration
        self.converged = False

    def run(
        self, max_iters: int, current_iter: int = 1, stop_at_convergence: bool = False
    ) -> int:
        if max_iters < 1:
            raise ValueError("Maximum amount of iterations must be >= 1")
        if current_iter < 1:
            raise ValueError("Current iteration must be >=1")
        self.iter = current_iter
        render_config_xml(self.context, self.experiment)
        while self.iter <= max_iters:
            print(f"Iteration {self.iter}")
            self.aoscm.run_coupled_model(schwarz_correction=bool(self.iter - 1))
            self._postprocess_iteration(next_iteration_exists=self.iter < max_iters)
            self.iter += 1
            if stop_at_convergence and self.converged:
                break

    def _postprocess_iteration(self, next_iteration_exists: bool):
        print(f"Postprocessing iteration {self.iter}")

        renamed_directory = self.run_directory.parent / f"{self.exp_id}_{self.iter}"
        self.run_directory.rename(renamed_directory)

        self.run_directory.mkdir()
        remapper = RemapCouplerOutput(
            renamed_directory,
            self.run_directory,
            self.experiment.cpl_scheme,
            self.experiment.dt_cpl,
            self.experiment.dt_ifs,
            self.experiment.dt_nemo,
            self.context.model_version,
        )
        remapper.remap()

        if self.iter > 1:
            local_conv, ampl_conv = self.convergence_checker.check_convergence(
                renamed_directory, self.run_directory
            )
            self.experiment.previous_iter_converged = {
                "local": local_conv,
                "amplitude": ampl_conv,
            }
            if local_conv and ampl_conv:
                self.converged = True
                print(f"Iteration {self.iter - 1} converged!")

        self.experiment.iteration = self.iter

        if self.reduce_output:
            if not next_iteration_exists:
                shutil.rmtree(self.run_directory)
            reduce_output(renamed_directory, keep_debug_output=False)
        serialize_experiment_setup(self.experiment, renamed_directory)
