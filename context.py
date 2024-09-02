from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Context:
    model_version: int
    platform: str
    model_dir: str | Path
    output_dir: str | Path
    template_dir: str | Path
    data_dir: str | Path
    plotting_dir: str | Path = None
    ecconf_executable: Path = field(init=False)
    runscript_dir: Path = field(init=False)
    config_run_template: Path = field(init=False)

    ascm_executable: Path = field(init=False)
    oscm_executable: Path = field(init=False)
    aoscm_executable: Path = field(init=False)
    aoscm_schwarz_correction_executable: Path = field(init=False)

    def __post_init__(self):
        if self.model_version not in (3,4):
            raise ValueError("Model version {self.model_version=} not supported")

        self.model_dir = Path(self.model_dir)
        self.data_dir = Path(self.data_dir)
        self.template_dir = Path(self.template_dir)

        if self.model_version == 3:
            self.config_run_template = self.template_dir / "config-run.xml.j2"
        else:
            self.config_run_template = self.template_dir / "config-run_ece4.xml.j2"
        
        self.ecconf_executable = self.model_dir / "sources/util/ec-conf/ec-conf"
        self.runscript_dir = self.model_dir / "runtime/scm-classic/PAPA"
        self.ascm_executable = self.runscript_dir / "ece4-scm_oifs.sh"
        self.oscm_executable = self.runscript_dir / "ece4-scm_nemo.sh"
        self.aoscm_executable = self.runscript_dir / "ece4-scm_oifs+nemo.sh"
        self.aoscm_schwarz_correction_executable = self.runscript_dir / "ece4-scm_oifs+nemo_schwarz_corr.sh"

        paths_to_check = [
            self.model_dir,
            self.data_dir,
            self.runscript_dir,
            self.config_run_template,
            self.ecconf_executable,
        ]

        for path in paths_to_check:
            if not path.exists():
                raise FileNotFoundError(f"Path does not exist: {path=}")            
        
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(exist_ok=True)
        if self.plotting_dir is not None:
            self.plotting_dir = Path(self.plotting_dir)
            self.plotting_dir.mkdir(exist_ok=True)
