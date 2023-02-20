import subprocess
from pathlib import Path

import pandas as pd
import yaml

import user_context as context
from utils.files import ChangeDirectory


class AOSCM:
    def __init__(self, runscript_dir: Path, ecconf_exe: Path, platform: str):
        self.runscript_dir = runscript_dir
        self.ecconf_executable = ecconf_exe
        self.platform = platform

    def _run_ecconf(self):
        with ChangeDirectory(context.runscript_dir):
            subprocess.run(
                [
                    self.ecconf_executable,
                    "-p",
                    self.platform,
                    "config-run.xml",
                ],
                capture_output=True,
            )

    def run_coupled_model(
        self, print_time: bool = False, schwarz_correction: bool = False
    ):
        self._run_ecconf()
        aoscm_executable = context.aoscm_executable
        if schwarz_correction:
            aoscm_executable = context.aoscm_schwarz_correction_executable
        self._run_model(aoscm_executable, print_time)

    def run_atmosphere_only(self, print_time: bool = False):
        self._run_ecconf()
        ascm_executable = context.ascm_executable
        self._run_model(ascm_executable, print_time)

    def run_ocean_only(self, print_time: bool = False):
        self._run_ecconf()
        oscm_executable = context.oscm_executable
        self._run_model(oscm_executable, print_time)

    def _run_model(self, executable: str, print_time: bool = False) -> None:
        print("Running model...")
        with ChangeDirectory(context.runscript_dir):
            completed_process = subprocess.run(
                [],
                executable=executable,
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
    with open(run_directory / "setup_dict.yaml", "w") as output_file:
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
