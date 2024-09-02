from pathlib import Path

platform = "pc-gcc-openmpi"
model_dir = Path("/home/valentina/dev/ece-scm")
output_dir = Path("/home/valentina/dev/scm_rundir/PAPA")
template_data_dir = Path("templates")
plotting_dir = Path("/home/valentina/dev/scm_rundir/plots")

runscript_dir = model_dir / "runtime/scm-classic/PAPA"
ecconf_executable = model_dir / "sources/util/ec-conf/ec-conf"

data_dir = runscript_dir / "data"
ifs_input_files_dir = data_dir / "oifs"
nemo_input_files_dir = data_dir / "nemo/init"
lim_input_files_dir = data_dir / "lim"
rstas_dir = data_dir / "oasis"
rstos_dir = data_dir / "oasis"

# where is the config-run.xml template (as a string!):
config_run_template = template_data_dir / "config-run.xml.j2"

# run scripts
ascm_executable = runscript_dir / "ece-scm_oifs.sh"
oscm_executable = runscript_dir / "ece-scm_nemo.sh"
aoscm_executable = runscript_dir / "ece-scm_oifs+nemo.sh"
aoscm_schwarz_correction_executable = runscript_dir / "ece-scm_oifs+nemo_2.sh"


def check_paths_exist():
    """List all defined paths which are not found on the system."""
    paths_to_check = [
        model_dir,
        output_dir,
        template_data_dir,
        plotting_dir,
        runscript_dir,
        ecconf_executable,
        data_dir,
        ifs_input_files_dir,
        nemo_input_files_dir,
        lim_input_files_dir,
        rstas_dir,
        rstos_dir,
        config_run_template,
    ]

    all_paths_exist = True
    for path in paths_to_check:
        if not path.exists():
            print(f"Warning! Path does not exist: {path=}")
            all_paths_exist = False

    if all_paths_exist:
        print("All paths were found!")


if __name__ == "__main__":

    check_paths_exist()
