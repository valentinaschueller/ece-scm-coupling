from pathlib import Path

platform = "valentinair"
model_dir = Path("/Users/valentina/dev/aoscm")
output_dir = Path("/Users/valentina/dev/aoscm_rundir/PAPA")

runscript_dir = model_dir / "runtime/scm-classic/PAPA"
ecconf_executable = model_dir / "sources/util/ec-conf/ec-conf"

data_dir = runscript_dir / "data"
ifs_input_files_dir = data_dir / "oifs/input_files"
nemo_input_files_dir = data_dir / "nemo/init/init_from_CMEMS"
rstas_dir = data_dir / "oasis/rstas_from_AMIP"
rstos_dir = data_dir / "oasis/rstos_from_CMEMS"