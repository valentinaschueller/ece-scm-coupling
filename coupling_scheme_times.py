import helpers as hlp
from helpers import ChangeDirectory, get_template

def generate_experiments(
    exp_prefix: str, dt_cpl: int, dt_ifs: int, dt_nemo: int, cpl_schemes: list
):
    exp_setups = []
    for cpl_scheme in cpl_schemes:
        dct = {
            "exp_id": f"{exp_prefix}{cpl_scheme}",
            "dt_cpl": dt_cpl,
            "dt_nemo": dt_nemo,
            "dt_ifs": dt_ifs,
            "cpl_scheme": cpl_scheme,
        }
        exp_setups.append(dct)
    return exp_setups

dt_cpl = 3600
cpl_schemes = [0, 1, 2]
exp_prefix = "CPL"
dt_ifs = 900
dt_nemo = 1800
experiments = generate_experiments(exp_prefix, dt_cpl, dt_ifs, dt_nemo, cpl_schemes)

config_template = get_template("config-run.xml.j2")
dst_folder = "../aoscm/runtime/scm-classic/PAPA"

for experiment in experiments:
    with ChangeDirectory(dst_folder):
        with open("./config-run.xml", "w") as config_out:
            config_out.write(
                config_template.render(
                    setup_dict=experiment,
                )
            )
    print(f"Config: {experiment['exp_id']}")
    hlp.run_model(print_time=True)
