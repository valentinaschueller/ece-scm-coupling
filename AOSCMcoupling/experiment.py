from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class Experiment:
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
    with_ice: bool = False
    ifs_nstrtini: int = 1
    ifs_leocwa: bool = False
    ice_input_file: Path | str = None
    cpl_scheme: int = 0
    ifs_levels: int = 60
    ifs_legwwms: bool = True
    ifs_lecumf: bool = True
    ifs_nradfr: int = 1
    iteration: int = None
    previous_iter_converged: dict[str, bool] = None

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

        for path in paths:
            if not path.exists():
                raise FileNotFoundError(f"{path} does not exist.")

        if self.cpl_scheme not in (0, 1, 2):
            raise ValueError(f"Coupling scheme {self.cpl_scheme} not available.")

        if self.ifs_levels not in (60, 137):
            raise ValueError(f"This number of levels is not supported.")
