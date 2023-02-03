from pathlib import Path

import pandas as pd

import helpers as hlp
from helpers import ChangeDirectory, get_template
from schwarz_coupling import SchwarzCoupling


def compute_nstrtini(
    simulation_start_date: pd.Timestamp,
    forcing_start_date: pd.Timestamp,
    forcing_dt_hours: int = 6,
) -> int:
    delta = (simulation_start_date - forcing_start_date).total_seconds()
    nstrtini = (delta / (forcing_dt_hours * 3600)) + 1
    if abs(int(nstrtini) - nstrtini) > 1e-10:
        raise ValueError("Start date is not available in forcing file!")
    return int(nstrtini)


cpl_schemes = [0, 1, 2]
dt_cpl = 14400
dt_ifs = 300
dt_nemo = 1800
max_iters = 60
exp_prefix = "M4S"

forcing_start_date = pd.Timestamp("2014-07-01")
start_date = pd.Timestamp("2014-07-01")
end_date = start_date + pd.Timedelta(5, "days")

nstrtini = compute_nstrtini(start_date, forcing_start_date)

config_template = get_template("config-run.xml.j2")
dst_folder = "../aoscm/runtime/scm-classic/PAPA"

experiment = {
    "dt_cpl": dt_cpl,
    "dt_nemo": dt_nemo,
    "dt_ifs": dt_ifs,
    "ifs_leocwa": "F",
    "ifs_nradfr": -1,
    "ifs_nstrtini": nstrtini,
    "schwarz_averaging": 1,
    "run_start_date": str(start_date),
    "run_end_date": str(end_date),
}


def run_naive_experiments():
    for cpl_scheme in cpl_schemes:
        experiment["exp_id"] = f"{exp_prefix}{cpl_scheme}"
        experiment["cpl_scheme"] = cpl_scheme
        print(f"Config: {experiment['exp_id']}")
        with ChangeDirectory(dst_folder):
            with open("./config-run.xml", "w") as config_out:
                config_out.write(
                    config_template.render(
                        setup_dict=experiment,
                    )
                )
        hlp.run_model()
        run_directory = Path("PAPA") / experiment["exp_id"]
        hlp.clean_model_output(run_directory)


def run_schwarz_experiments():
    cpl_scheme = 0
    experiment["cpl_scheme"] = cpl_scheme
    experiment["exp_id"] = f"{exp_prefix}{cpl_scheme}"
    schwarz_exp = SchwarzCoupling(experiment_dict=experiment)
    schwarz_exp.run(max_iters, 40)


if __name__ == "__main__":

    # run_naive_experiments()

    run_schwarz_experiments()
