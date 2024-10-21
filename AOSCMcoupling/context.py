from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Context:
    """Model context for AOSCM experiments on a specific system.

    Dataclass collecting paths relevant for running (multiple) experiments.
    Data in here is expected to be the same for all your experiments.

    :raises ValueError: if model version is not supported
    :raises FileNotFoundError: if a provided path does not exist
    (except for output_dir, which will be created if it does not exist.)
    """

    model_version: int
    platform: str
    model_dir: str | Path
    output_dir: str | Path
    template_dir: str | Path
    data_dir: str | Path

    ifs_version: str = "43r3v1.ref"
    
    ecconf_executable: Path = field(init=False)
    runscript_dir: Path = field(init=False)
    config_run_template: Path = field(init=False)

    ascm_executable: Path = field(init=False)
    oscm_executable: Path = field(init=False)
    aoscm_executable: Path = field(init=False)
    aoscm_schwarz_correction_executable: Path = field(init=False)

    def __post_init__(self):
        if self.model_version not in (3, 4):
            raise ValueError("Model version {self.model_version=} not supported")

        self.model_dir = Path(self.model_dir)
        self.data_dir = Path(self.data_dir)
        self.template_dir = Path(self.template_dir)

        if self.model_version == 3:
            self.config_run_template = self.template_dir / "config-run.xml.j2"
            prefix = "ece"
        else:
            self.config_run_template = self.template_dir / "config-run_ece4.xml.j2"
            prefix = "ece4"
        
        if self.ifs_version not in ("43r3v1.ref", "40r1v1.1.ref"):
            raise ValueError("Unsupported IFS version")

        self.ecconf_executable = self.model_dir / "sources/util/ec-conf/ec-conf"
        self.runscript_dir = self.model_dir / "runtime/scm-classic/PAPA"
        self.ascm_executable = self.runscript_dir / f"{prefix}-scm_oifs.sh"
        self.oscm_executable = self.runscript_dir / f"{prefix}-scm_nemo.sh"
        self.aoscm_executable = self.runscript_dir / f"{prefix}-scm_oifs+nemo.sh"
        self.aoscm_schwarz_correction_executable = (
            self.runscript_dir / f"{prefix}-scm_oifs+nemo_schwarz_corr.sh"
        )

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
