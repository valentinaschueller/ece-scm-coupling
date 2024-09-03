import subprocess
from pathlib import Path

import pandas as pd
from ruamel.yaml import YAML

from AOSCMcoupling.context import Context
from AOSCMcoupling.files import ChangeDirectory


class AOSCM:
    """Python wrapper to run an EC-Earth AOSCM experiment.

    The class takes care of running `ec-conf` as well as calling the correct run script inside `runscript_dir`.
    We assume that the experiment is already configured correctly with `config-run.xml` inside the `runscript_dir`.
    """

    def __init__(self, context: Context):
        self.context = context

    def _run_ecconf(self):
        with ChangeDirectory(self.context.runscript_dir):
            subprocess.run(
                [
                    self.context.ecconf_executable,
                    "-p",
                    self.context.platform,
                    "config-run.xml",
                ],
                capture_output=True,
            )

    def run_coupled_model(
        self, print_time: bool = False, schwarz_correction: bool = False
    ):
        """run the EC-Earth AOSCM in coupled mode.

        :param print_time: print wall clock time at the end of the run, defaults to False
        :type print_time: bool, optional
        :param schwarz_correction: whether to use the Schwarz correction run script, defaults to False
        :type schwarz_correction: bool, optional
        """
        self._run_ecconf()
        aoscm_executable = self.context.aoscm_executable
        if schwarz_correction:
            aoscm_executable = self.context.aoscm_schwarz_correction_executable
        self._run_model(aoscm_executable, print_time)

    def run_atmosphere_only(self, print_time: bool = False):
        """do an atmosphere-only run of the EC-Earth AOSCM.

        :param print_time: print wall clock time at the end of the run, defaults to False
        :type print_time: bool, optional
        """
        self._run_ecconf()
        ascm_executable = self.context.ascm_executable
        self._run_model(ascm_executable, print_time)

    def run_ocean_only(self, print_time: bool = False):
        """do an ocean-only run of the EC-Earth AOSCM.

        :param print_time: print wall clock time at the end of the run, defaults to False
        :type print_time: bool, optional
        """
        self._run_ecconf()
        oscm_executable = self.context.oscm_executable
        self._run_model(oscm_executable, print_time)

    def _run_model(self, executable: Path, print_time: bool = False) -> None:
        print("Running model...")
        args = [str(executable)]
        with ChangeDirectory(self.context.runscript_dir):
            completed_process = subprocess.run(
                args,
                capture_output=True,
                text=print_time,  # if print_time, we want stdout and stderr to be string instead of bytes.
            )
        print("Model run complete.")
        if not print_time:
            return
        output = completed_process.stdout.splitlines()
        for line in output:
            if "Finished leg" in line:
                print(line)


def reduce_output(run_directory: Path, keep_debug_output: bool = True) -> None:
    """
    remove all AOSCM output which is irrelevant for further analysis.
    """
    output_files = list(run_directory.glob("*"))
    output_files_to_remove = []
    for output_file in output_files:
        if "diagvar" in output_file.name:
            continue
        if "progvar" in output_file.name:
            continue
        if "_grid_" in output_file.name:
            continue
        if "_icemod" in output_file.name:
            continue
        if "namelist_" in output_file.name:
            continue
        if output_file.name == "namcouple":
            continue
        if output_file.name == "fort.4":
            continue
        if keep_debug_output:
            if "debug" in output_file.name:
                continue
            if output_file.name == "nout.000000":
                continue
        output_files_to_remove.append(output_file)

    for file in output_files_to_remove:
        file.unlink()


def serialize_experiment_setup(experiment: dict, run_directory: Path):
    yaml = YAML(typ="unsafe", pure=True)
    with open(run_directory / "setup_dict.yaml", "w") as output_file:
        yaml = YAML(typ="unsafe", pure=True)
        yaml.dump(experiment, output_file)


def compute_nstrtini(
    simulation_start_date: pd.Timestamp,
    forcing_start_date: pd.Timestamp,
    forcing_dt_hours: int = 6,
) -> int:
    delta = (simulation_start_date - forcing_start_date).total_seconds()
    if delta < 0:
        raise ValueError("Start date is earlier than first value of forcing file!")
    nstrtini = (delta / (forcing_dt_hours * 3600)) + 1
    if abs(int(nstrtini) - nstrtini) > 1e-10:
        raise ValueError("Start date is not available in forcing file!")
    return int(nstrtini)
