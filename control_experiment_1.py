from pathlib import Path

import helpers as hlp
from helpers import ChangeDirectory, get_template
from schwarz_coupling import SchwarzCoupling

cpl_schemes = [0, 1, 2]
dt_cpl = 3600
dt_ifs = 900
dt_nemo = 900
max_iters = 20
exp_prefix_naive = "C1N"
exp_prefix_schwarz = "C1S"

config_template = get_template("config-run.xml.j2")
dst_folder = "../aoscm/runtime/scm-classic/PAPA"

experiment = {
    "dt_cpl": dt_cpl,
    "dt_nemo": dt_nemo,
    "dt_ifs": dt_ifs,
    "ifs_leocwa": "F",
}


def run_naive_experiments():
    for cpl_scheme in cpl_schemes:
        experiment["exp_id"] = f"{exp_prefix_naive}{cpl_scheme}"
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

    for cpl_scheme in cpl_schemes:
        exp_id = f"{exp_prefix_schwarz}{cpl_scheme}"
        schwarz_exp = SchwarzCoupling(exp_id, dt_cpl, dt_ifs, dt_nemo, cpl_scheme)
        schwarz_exp.run(max_iters)


if __name__ == "__main__":

    run_naive_experiments()

    run_schwarz_experiments()
