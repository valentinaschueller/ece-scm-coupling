import pandas as pd

import user_context as context
import utils.helpers as hlp
from schwarz_coupling import SchwarzCoupling
from utils.templates import render_config_xml

dt_cpl = 3600
dt_ifs = 720
dt_nemo = 1800
max_iters = 25

cpl_schemes = [1, 2]
exp_prefix = "RA"

nradfr_dict = {
    "L": -3,
    "E": -1,
    "S": 1,
}

forcing_start_date = pd.Timestamp("2014-07-01")
start_date = pd.Timestamp("2014-07-01")
end_date = start_date + pd.Timedelta(4, "days")

nstrtini = hlp.compute_nstrtini(start_date, forcing_start_date)

experiment = {
    "dt_cpl": dt_cpl,
    "dt_nemo": dt_nemo,
    "dt_ifs": dt_ifs,
    "ifs_leocwa": "F",
    "ifs_nstrtini": nstrtini,
    "run_start_date": str(start_date),
    "run_end_date": str(end_date),
}


def run_naive_experiments():
    for freq_id, freq in nradfr_dict.items():
        experiment["ifs_nradfr"] = freq
        for cpl_scheme in cpl_schemes:
            experiment["cpl_scheme"] = cpl_scheme
            experiment["exp_id"] = f"{exp_prefix}{freq_id}{cpl_scheme}"

            print(f"Config: {experiment['exp_id']}")
            render_config_xml(
                context.runscript_dir, context.config_run_template, experiment
            )
            hlp.run_model()
            run_directory = context.output_dir / experiment["exp_id"]
            hlp.clean_model_output(run_directory)


def run_schwarz_experiments():
    cpl_scheme = 0
    experiment["cpl_scheme"] = cpl_scheme
    for freq_id, freq in nradfr_dict.items():
        experiment["ifs_nradfr"] = freq
        experiment["exp_id"] = f"{exp_prefix}{freq_id}{cpl_scheme}"
        schwarz_exp = SchwarzCoupling(experiment_dict=experiment)
        schwarz_exp.run(max_iters)


if __name__ == "__main__":

    run_naive_experiments()

    run_schwarz_experiments()
