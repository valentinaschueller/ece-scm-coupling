# Running the AOSCM with Python

You can set up and run the model from a Python script or Jupyter notebook.
To begin with, you need to set up the user context on your system, which contains basic information about your platform, file system, and installed model.

## Setting up the user context

Here is an example for how this might look like on your system:

```python 
from AOSCMcoupling import Context
context = Context(
    platform="pc-gcc-openmpi",
    model_version=3,
    model_dir="/home/valentina/dev/aoscm/ece3-scm",
    output_dir="/home/valentina/dev/aoscm/experiments/PAPA",
    template_dir="/home/valentina/dev/aoscm/scm-coupling/templates",
    data_dir="/home/valentina/dev/aoscm/initial_data/control_experiment",
)
```

You should be able to reuse the context for all experiments you run on one system.
When you create your `Context` object, it automatically checks that the provided paths exist (except for `output_dir` which will be created in case it does not exist) and converts them to [`Path`](https://docs.python.org/3/library/pathlib.html) objects.

## Setting up an experiment

As described in the [EC-Earth SCM documentation](https://dev.ec-earth.org/projects/ecearth3/wiki/Single_Column_Coupled_EC-Earth#Running-the-model), one would normally set up an experiment using the XML parameters in `config-run.xml`.
The scripts in this repository allow us to generate such an XML file directly from Python.
For this, we instantiate an `Experiment`, which contains, e.g.:
- the input files for OpenIFS, NEMO, and OASIS (these can be generated, e.g., using the AOSCMtools package)
- time step sizes for NEMO, OpenIFS
- the simulation length and start date
- the coupling method: parallel, atmosphere-first, and ocean-first (0, 1, 2)

Additionally, the `Experiment` can be used to turn common OpenIFS parameterizations on/off, e.g., the warm layer effect.

Here is an example for setting up an experiment:

```python
from AOSCMcoupling import Experiment
import pandas as pd

experiment = Experiment(
    dt_cpl=3600,
    dt_ifs=900,
    dt_nemo=900,
    exp_id="TEST",
    ifs_leocwa=False,
    with_ice=False,
    nem_input_file=context.data_dir / "nemo_papa_2014-07-01.nc",
    ifs_input_file=context.data_dir / "oifs_papa_2014-07-01_30.nc",
    oasis_rstas=context.data_dir / "rstas_2014-07-01_00_era.nc",
    oasis_rstos=context.data_dir / "rstos_2014-07-01.nc",
    run_start_date=pd.Timestamp("2014-07-01"),
    run_end_date=pd.Timestamp("2014-07-05"),
    ifs_nstrtini=1,
    cpl_scheme=0,
)
```

The context and experiment are handed to a templated version of `config-run.xml`, examples are given in `templates`.
Using [Jinja](https://jinja.palletsprojects.com/) and the template file, a valid XML file can be generated as follows:

```python
from AOSCMcoupling import render_config_xml

render_config_xml(context, experiment)
```

After this, the rendered version of the template file at `context.config_run_template` will be placed inside `context.runscript_dir`.

## Running an Experiment

To run the EC-Earth AOSCM, one would usually have to do two steps from inside the model directory:
1. Run `ec-conf` to generate shell scripts and namelists using the parameters supplied in `config-run.xml`.
2. Run one of the generated shell scripts.

Both tasks are abstracted away into the `AOSCM` class inside `helpers.py`.
Assuming the experiment has already been configured as described above, one can do a coupled run of the AOSCM as follows:

```python
from AOSCMcoupling AOSCM
aoscm = AOSCM(context)
aoscm.run_coupled_model() # or, e.g., aoscm.run_atmosphere_only()
```

It is also possible to reduce the amount of output after a simulation:

```python
from AOSCMcoupling import reduce_output

reduce_output(
    context.output_dir / experiment.exp_id, keep_debug_output=False
)
```