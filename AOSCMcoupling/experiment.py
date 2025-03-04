from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from ruamel.yaml import YAML


@dataclass
class Experiment:
    """Wrapper for data necessary to set up an AOSCM experiment

    :raises FileNotFoundError: if any of the initial data files is not found
    :raises ValueError: if cpl_scheme or ifs_levels not supported
    """

    dt_cpl: int
    dt_nemo: int
    dt_ifs: int
    run_start_date: pd.Timestamp | str
    run_end_date: pd.Timestamp | str
    nem_input_file: Path | str
    ifs_input_file: Path | str
    oasis_rstas: Path | str
    oasis_rstos: Path | str
    exp_id: str
    ifs_nstrtini: int = 1
    ifs_leocwa: bool = False
    cpl_scheme: int = 0
    ifs_levels: int = 60
    ifs_legwwms: bool = True
    ifs_lecumf: bool = True
    ifs_nradfr: int = 1
    with_ice: bool = False
    dt_ice: int = None
    ice_input_file: Path | str = None
    ice_alb_sdry: float = 0.85
    ice_alb_smlt: float = 0.75
    ice_alb_idry: float = 0.60
    ice_alb_imlt: float = 0.50
    ice_alb_dpnd: float = 0.27
    ice_cnd_s: float = 0.31
    ice_hinew: float = 0.1
    ice_nlay_i: int = 2
    ice_jpl: int = 5
    iteration: int = None
    iterate_converged: dict[str, bool] = None

    def __post_init__(self):
        self.nem_input_file = Path(self.nem_input_file)
        self.ifs_input_file = Path(self.ifs_input_file)
        self.oasis_rstas = Path(self.oasis_rstas)
        self.oasis_rstos = Path(self.oasis_rstos)
        paths = [
            self.ifs_input_file,
            self.nem_input_file,
            self.oasis_rstas,
            self.oasis_rstos,
        ]
        if self.with_ice:
            self.ice_input_file = Path(self.ice_input_file)
            paths.append(self.ice_input_file)
        if self.dt_ice is None:
            self.dt_ice = self.dt_nemo

        for path in paths:
            if not path.exists():
                raise FileNotFoundError(f"{path} does not exist.")

        if self.cpl_scheme not in (0, 1, 2):
            raise ValueError(f"Coupling scheme {self.cpl_scheme} not available.")

        if self.ifs_levels not in (60, 137):
            raise ValueError("This number of levels is not supported.")

    def to_yaml(self, file: Path):
        with open(file, "w") as file:
            yaml = YAML(typ="unsafe", pure=True)
            yaml.dump(self, file)
