import subprocess
from pathlib import Path

import pandas as pd

from utils.files import ChangeDirectory


class AOSCM:
    def __init__(
        self, runscript_dir: Path, ecconf_exe: Path, run_dir: Path, platform: str
    ):
        self.runscript_dir = runscript_dir
        self.ecconf_executable = ecconf_exe
        self.run_directory = run_dir
        self.platform = platform

    def _run_ecconf(self):
        with ChangeDirectory(self.runscript_dir):
            subprocess.run(
                [
                    str(self.ecconf_executable),
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
        aoscm_executable = "./ece-scm_oifs+nemo.sh"
        if schwarz_correction:
            aoscm_executable = "./ece-scm_oifs+nemo_2.sh"
        self._run_model(aoscm_executable, print_time)

    def run_atmosphere_only(self, print_time: bool = False):
        self._run_ecconf()
        ascm_executable = "./ece-scm_oifs.sh"
        self._run_model(ascm_executable, print_time)

    def run_ocean_only(self, print_time: bool = False):
        self._run_ecconf()
        oscm_executable = "./ece-scm_nemo.sh"
        self._run_model(oscm_executable, print_time)

    def _run_model(self, executable: str, print_time: bool = False) -> None:
        with ChangeDirectory(self.runscript_dir):
            print("Running model...")
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

    def reduce_output(self, keep_debug_output: bool = True) -> None:
        """
        remove some AOSCM output files which are irrelevant for further analysis.
        """
        for path in self.run_directory.glob("SO4*"):
            path.unlink()
        for path in self.run_directory.glob("*.exe"):
            path.unlink()
        for path in self.run_directory.glob("*CLIM"):
            path.unlink()
        for path in self.run_directory.glob("RAD*"):
            path.unlink()
        for path in self.run_directory.glob("*.lnk"):
            path.unlink()
        (self.run_directory / "onecol.r").unlink(missing_ok=True)
        (self.run_directory / "K1rowdrg.nc").unlink(missing_ok=True)
        (self.run_directory / "M2rowdrg.nc").unlink(missing_ok=True)
        (self.run_directory / "fort.20").unlink(missing_ok=True)
        (self.run_directory / "scm_in.nc").unlink(missing_ok=True)
        (self.run_directory / "time.step").unlink(missing_ok=True)
        (self.run_directory / "vtable").unlink(missing_ok=True)
        (self.run_directory / "ECOZC").unlink(missing_ok=True)
        (self.run_directory / "MCICA").unlink(missing_ok=True)
        if keep_debug_output:
            return
        (self.run_directory / "debug.01.000000").unlink(missing_ok=True)
        (self.run_directory / "debug.02.000000").unlink(missing_ok=True)
        (self.run_directory / "nout.000000").unlink(missing_ok=True)


def run_model(
    print_time: bool = False, executable: str = "./ece-scm_oifs+nemo.sh"
) -> None:
    """
    runs the EC-Earth SCM. If print_time=True, the output line summarizing the simulation time is printed.
    """
    with ChangeDirectory("../aoscm/runtime/scm-classic/PAPA"):
        print("Running model")
        subprocess.run(
            [
                "/Users/valentina/dev/aoscm/sources/util/ec-conf/ec-conf",
                "-p",
                "valentinair",
                "config-run.xml",
            ],
            capture_output=True,
        )
        completed_process = subprocess.run(
            [],
            executable=executable,
            capture_output=True,
            text=print_time,  # if print_time, we want stdout and stderr to be string instead of bytes.
        )
        print("Model run complete")
        if not print_time:
            return
        output = completed_process.stdout.splitlines()
        for line in output:
            if "Finished leg" in line:
                print(line)


def clean_model_output(run_directory: Path) -> None:
    """
    remove some AOSCM output files which are irrelevant for further analysis.
    """
    for path in run_directory.glob("SO4*"):
        path.unlink()
    for path in run_directory.glob("*.exe"):
        path.unlink()
    for path in run_directory.glob("*CLIM"):
        path.unlink()
    for path in run_directory.glob("RAD*"):
        path.unlink()
    for path in run_directory.glob("*.lnk"):
        path.unlink()
    (run_directory / "onecol.r").unlink(missing_ok=True)
    (run_directory / "K1rowdrg.nc").unlink(missing_ok=True)
    (run_directory / "M2rowdrg.nc").unlink(missing_ok=True)
    (run_directory / "debug.01.000000").unlink(missing_ok=True)
    (run_directory / "debug.02.000000").unlink(missing_ok=True)
    (run_directory / "nout.000000").unlink(missing_ok=True)
    (run_directory / "fort.20").unlink(missing_ok=True)
    (run_directory / "scm_in.nc").unlink(missing_ok=True)
    (run_directory / "time.step").unlink(missing_ok=True)
    (run_directory / "vtable").unlink(missing_ok=True)
    (run_directory / "ECOZC").unlink(missing_ok=True)
    (run_directory / "MCICA").unlink(missing_ok=True)


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