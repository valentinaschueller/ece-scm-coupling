# Running the AOSCM with Python

In this tutorial and all others, we make use of `user_context.py`, which contains paths for your local environment.
**Before using any of the scripts, make sure to update this file accordingly!**
To test if all paths inside `user_context.py` exist, run it from the command line:

```
> python3 user_context.py
All paths were found!
```

## Configuring an Experiment

As described in the [EC-Earth SCM documentation](https://dev.ec-earth.org/projects/ecearth3/wiki/Single_Column_Coupled_EC-Earth#Running-the-model), one would normally set up an experiment using the XML parameters in `config-run.xml`.
The scripts in this repository allow us to generate such an XML file directly from Python.
For this, a dictionary is filled with common simulation parameters:
- the input files for OpenIFS, NEMO, and OASIS (see [this page](02_input_files.md))
- time step sizes for NEMO, OpenIFS
- the simulation length and start date
- the coupling method: parallel, atmosphere-first, and ocean-first (0, 1, 2)

Additionally, the dictionary can be used to turn common OpenIFS parameterizations on/off, e.g., the warm layer effect.

This dictionary is supplied to a templated version of `config-run.xml`, an example is given in `templates/config-run.xml.j2`.
Using [Jinja](https://jinja.palletsprojects.com/) and the template file, a valid XML file can be generated as follows:

```python
from utils.templates import render_config_xml
import user_context as context

experiment = {
    "exp_id": "EXP0",
    "dt_cpl": 3600,
    # ...
    "cpl_scheme": 0,
}
render_config_xml(context.runscript_dir, context.config_run_template, experiment)
```

After this, the rendered version of the template file at `context.config_run_template` will be placed inside `context.runscript_dir`.

## Running an Experiment

To run the EC-Earth AOSCM, one would usually have to do two steps from inside the model directory:
1. Run `ec-conf` to generate shell scripts and namelists using the parameters supplied in `config-run.xml`.
2. Run one of the generated shell scripts.

Both tasks are abstracted away into the `AOSCM` class inside `utils/helpers.py`.
Assuming the experiment has already been configured as described above, one can do a coupled run of the AOSCM as follows:

```python
from utils.helpers import AOSCM

aoscm = AOSCM(
    context.runscript_dir,
    context.ecconf_executable,
    context.platform,
)
aoscm.run_coupled_model() # or, e.g., aoscm.run_atmosphere_only()
```

It is also possible to reduce the amount of output after a simulation:

```python
from utils.helpers import reduce_output

reduce_output(
    context.output_dir / experiment["exp_id"], keep_debug_output=False
)
```