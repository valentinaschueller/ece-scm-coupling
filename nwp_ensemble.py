import shutil
from pathlib import Path

import pandas as pd

from context import Context
from schwarz_coupling import SchwarzCoupling
from setup_experiment import set_experiment_date_properties, set_experiment_input_files
from utils.helpers import AOSCM, reduce_output, serialize_experiment_setup
from utils.templates import render_config_xml

context = Context(
    platform="pc-gcc-openmpi",
    model_version=3,
    model_dir="/home/valentina/dev/aoscm/ece3-scm",
    output_dir="/home/valentina/dev/aoscm/scm_rundir",
    template_dir="/home/valentina/dev/aoscm/scm_rundir/templates",
    plotting_dir="/home/valentina/dev/aoscm/scm_rundir/plots",
    data_dir="/home/valentina/dev/aoscm/initial_data/nwp",
)

start_dates = pd.date_range(
    pd.Timestamp("2014-07-03 00:00:00"), pd.Timestamp("2014-07-28 18:00:00"), freq="6H"
)
simulation_time = pd.Timedelta(2, "days")

ifs_input_file_start_date = pd.Timestamp("2014-07-01")
ifs_input_file_freq = pd.Timedelta(6, "hours")

dt_ifs = 720
dt_nemo = 1800
dt_cpl = 3600
ifs_nradfr = -1
ifs_leocwa = "F"
exp_id = "ENSB"
run_directory = context.output_dir / exp_id

coupling_scheme_to_name = {
    0: "parallel",
    1: "atm-first",
    2: "oce-first",
}

max_iters = 20

ensemble_directory = context.output_dir / "ensemble_output"


sources = ["par", "atm", "oce"]

non_converged_experiments = []

if __name__ == "__main__":

    ensemble_directory.mkdir(exist_ok=True)

    aoscm = AOSCM(context)

    experiment = {
        "dt_cpl": dt_cpl,
        "dt_nemo": dt_nemo,
        "dt_ifs": dt_ifs,
        "ifs_leocwa": "F",
        "exp_id": exp_id,
    }
    for start_date in start_dates:
        start_date_string = f"{start_date.date()}_{start_date.hour:02}"
        start_date_directory = ensemble_directory / start_date_string
        start_date_directory.mkdir(exist_ok=True)
        for source in sources:
            (start_date_directory / source).mkdir(exist_ok=True)

        set_experiment_date_properties(
            experiment,
            start_date,
            simulation_time,
            ifs_input_file_start_date,
            ifs_input_file_freq,
        )

        for source in sources:
            set_experiment_input_files(experiment, start_date, source)

            experiment["iteration"] = None
            experiment["previous_iter_converged"] = None

            for coupling_scheme, cpl_scheme_name in coupling_scheme_to_name.items():
                experiment["cpl_scheme"] = coupling_scheme
                render_config_xml(context, experiment)
                aoscm.run_coupled_model()
                reduce_output(run_directory, keep_debug_output=False)
                serialize_experiment_setup(experiment, run_directory)
                new_directory = start_date_directory / source / cpl_scheme_name
                run_directory.rename(new_directory)

            experiment["cpl_scheme"] = 0
            schwarz = SchwarzCoupling(experiment)
            schwarz.run(max_iters, stop_at_convergence=True)
            new_directory = start_date_directory / source / "schwarz"
            converged_schwarz_dir = Path(f"{schwarz.run_directory}_{schwarz.iter - 2}")
            converged_schwarz_dir.rename(new_directory)
            for iter in range(1, schwarz.iter - 2):
                nonconverged_schwarz_dir = Path(f"{schwarz.run_directory}_{iter}")
                shutil.rmtree(nonconverged_schwarz_dir)
            final_schwarz_dir = Path(f"{schwarz.run_directory}_{schwarz.iter - 1}")
            shutil.rmtree(final_schwarz_dir)
            if not schwarz.converged:
                non_converged_experiments.append(experiment.copy())

    print("Experiments which did not converge:")
    print(non_converged_experiments)

    if run_directory.exists():
        shutil.rmtree(run_directory)
