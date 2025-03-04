import shutil
import warnings

from AOSCMcoupling.context import Context
from AOSCMcoupling.convergence_checker import ConvergenceChecker
from AOSCMcoupling.experiment import Experiment
from AOSCMcoupling.helpers import AOSCM, reduce_output
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
        self.output_dir = context.output_dir
        self.run_directory = context.output_dir / self.exp_id
        self.aoscm = AOSCM(context)
        self.convergence_checker = ConvergenceChecker()
        self.reduce_output = reduce_output_after_iteration
        self.converged = False

    def run(
        self,
        max_iters: int,
        current_iter: int = 1,
        stop_at_convergence: bool = False,
        rel_tol: float = 1e-3,
    ) -> int:
        if max_iters < 1:
            raise ValueError("Maximum amount of iterations must be >= 1")
        if current_iter < 1:
            raise ValueError("Current iteration must be >=1")
        self.iter = current_iter
        if self.iter > 1:
            self._prepare_restart()

        render_config_xml(self.context, self.experiment)
        while self.iter <= max_iters:
            print(f"Iteration {self.iter}")
            self.aoscm.run_coupled_model(schwarz_correction=bool(self.iter - 1))
            self._postprocess_iteration(self.iter < max_iters, rel_tol)
            self.iter += 1
            if stop_at_convergence and self.converged:
                break
        self.iter -= 1

    def _postprocess_iteration(self, next_iteration_exists: bool, rel_tol: float):
        print(f"Postprocessing iteration {self.iter}")

        current_iterate_dir = self.output_dir / f"{self.exp_id}_{self.iter}"
        if current_iterate_dir.exists():
            warnings.warn("Iteration already exists. Replacing contents!")
            shutil.rmtree(current_iterate_dir)
        self.run_directory.rename(current_iterate_dir)

        self.run_directory.mkdir()
        remapper = RemapCouplerOutput(
            current_iterate_dir,
            self.run_directory,
            self.experiment.cpl_scheme,
            self.experiment.dt_cpl,
            self.experiment.dt_ifs,
            self.experiment.dt_nemo,
            self.context.model_version,
        )
        remapper.remap()

        if self.iter > 1:
            previous_iterate_dir = self.output_dir / f"{self.exp_id}_{self.iter - 1}"
            reference_dir = self.output_dir / f"{self.exp_id}_1"

            conv_2_norm, conv_inf_norm = self.convergence_checker.check_convergence(
                current_iterate_dir, previous_iterate_dir, reference_dir, rel_tol
            )
            self.experiment.iterate_converged = {
                "2-norm": conv_2_norm,
                "inf-norm": conv_inf_norm,
            }
            if conv_2_norm and conv_inf_norm:
                self.converged = True
                print(f"Iteration {self.iter} converged!")

        self.experiment.iteration = self.iter

        if self.reduce_output:
            if not next_iteration_exists:
                shutil.rmtree(self.run_directory)
            reduce_output(current_iterate_dir, keep_debug_output=False)
        self.experiment.to_yaml(current_iterate_dir / "setup_dict.yaml")

    def _prepare_restart(self):
        previous_iterate_dir = self.output_dir / f"{self.exp_id}_{self.iter - 1}"
        if not previous_iterate_dir.exists():
            raise FileNotFoundError(
                f"Output data from iteration {self.iter - 1} not found!"
            )

        self.run_directory.mkdir(exist_ok=True)
        remapper = RemapCouplerOutput(
            previous_iterate_dir,
            self.run_directory,
            self.experiment.cpl_scheme,
            self.experiment.dt_cpl,
            self.experiment.dt_ifs,
            self.experiment.dt_nemo,
            self.context.model_version,
        )
        remapper.remap()
