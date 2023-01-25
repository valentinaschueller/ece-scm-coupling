import os
import subprocess
import warnings
from pathlib import Path

import iris
import iris.cube
import jinja2


def load_cube(filename: str, var: str) -> iris.cube.Cube:
    with warnings.catch_warnings():
        # Suppress warning for invalid units
        warnings.filterwarnings(
            action="ignore",
            category=UserWarning,
        )
        cube = iris.load_cube(filename, var)
    return cube


def load_cubes(filename: str) -> iris.cube.CubeList:
    with warnings.catch_warnings():
        # Suppress warning for invalid units
        warnings.filterwarnings(
            action="ignore",
            category=UserWarning,
        )
        cube = iris.load(filename)
    return cube


def get_template(template_filename: str) -> jinja2.Template:
    """get Jinja2 template file"""
    search_path = ["."]

    loader = jinja2.FileSystemLoader(search_path)
    environment = jinja2.Environment(loader=loader)
    return environment.get_template(template_filename)


# Using https://stackoverflow.com/revisions/13197763/9
class ChangeDirectory:
    """Context manager for changing the current working directory"""

    def __init__(self, new_path):
        self.new_path = Path(new_path).expanduser()
        self.saved_path = Path.cwd()

    def __enter__(self):
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)


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


def render_config_xml(
    destination: Path, config_template: jinja2.Template, experiment: dict
) -> None:
    if not destination.is_dir():
        raise TypeError(f"Destination is not a directory! {destination=}")
    with ChangeDirectory(destination):
        with open("./config-run.xml", "w") as config_out:
            config_out.write(
                config_template.render(
                    setup_dict=experiment,
                )
            )


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
