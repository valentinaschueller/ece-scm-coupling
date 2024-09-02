import pandas as pd

from context import Context
from schwarz_coupling import SchwarzCoupling
from setup_experiment import set_experiment_date_properties, set_experiment_input_files
from utils.helpers import AOSCM, reduce_output
from utils.templates import render_config_xml

context = Context(
    platform="cosmos",
    model_version=4,
    model_dir="/home/vschuller/aoscm",
    output_dir="/home/vschuller/rundir",
    template_dir="/home/vschuller/ece-scm-coupling/templates",
    plotting_dir="/home/vschuller/rundir/plots",
    data_dir="/home/schuller/initial_data/control_experiment",
)

cpl_scheme = 0
dt_cpl = 3600
dt_ifs = 900
dt_nemo = 900
max_iters = 20

start_date = pd.Timestamp("2010-06-15")
simulation_duration = pd.Timedelta(12, "hours")
ifs_input_start_date = pd.Timestamp("2010-06-15")
ifs_input_freq = pd.Timedelta(6, "hours")

experiment = {
    "dt_cpl": dt_cpl,
    "dt_nemo": dt_nemo,
    "dt_ifs": dt_ifs,
    "ifs_leocwa": "F",
}
set_experiment_date_properties(
    experiment, start_date, simulation_duration, ifs_input_start_date, ifs_input_freq
)
nem_input_file = context.nemo_input_files_dir / "init_PAPASTATION_2010-06-15.nc"
oifs_input_file = context.ifs_input_files_dir / "papa_20100615.nc"
oasis_rstas = context.rstas_dir / "rstas_2010-06-15.nc"
oasis_rstos = context.rstos_dir / "rstos_2010-06-15.nc"

assert nem_input_file.exists()
assert oifs_input_file.exists()
assert oasis_rstas.exists()
assert oasis_rstos.exists()

experiment["nem_input_file"] = nem_input_file
experiment["ifs_input_file"] = oifs_input_file
experiment["oasis_rstas"] = oasis_rstas
experiment["oasis_rstos"] = oasis_rstos

aoscm = AOSCM(context)


ifs_input_start_date = pd.Timestamp("2010-06-15")
ifs_input_freq = pd.Timedelta(6, "hours")

max_iters = 5

if __name__ == "__main__":

    for cpl_scheme in [0, 1, 2]:
        exp_id = f"TES{cpl_scheme}"
        experiment["exp_id"] = exp_id
        experiment["cpl_scheme"] = cpl_scheme
        print(f"Config: {experiment['exp_id']}")
        render_config_xml(context, experiment)
        aoscm.run_coupled_model()
        # reduce_output(run_directory=context.output_dir / exp_id)

    # cpl_scheme = 0
    # experiment["cpl_scheme"] = cpl_scheme
    # exp_id = "TESS"
    # experiment["exp_id"] = exp_id

    # schwarz_exp = SchwarzCoupling(experiment, reduce_output_after_iteration=True)
    # schwarz_exp.run(max_iters)
