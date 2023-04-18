# Schwarz Waveform Relaxation with the EC-Earth AOSCM

Schwarz waveform relaxation (SWR) is taken care of by the class `SchwarzCoupling` in the module `schwarz_coupling.py`.
Prerequisites before you can run an SWR experiment:
- The EC-Earth AOSCM is already compiled on your system.
- The paths in `user_context.py` are set correctly. (Use `python3 user_context.py` as a first indication that all paths exist)
- Initial and forcing files for your experiment are available.
- The runscript directory (`runscript_dir` in `user_context.py`) contains scripts for a regular coupled run *and* the Schwarz correction.

The first three bullet points can be checked by running a basic AOSCM experiment, as described in the [respective tutorial](01_basic_aoscm_experiment.md).
A minimal Python script for an SWR simulation looks as follows:

```python
from schwarz_coupling import SchwarzCoupling

experiment = {
    "exp_id": "EXP0",
    "dt_cpl": 3600,
    # ... paths to input files, coupling scheme, etc.
}
schwarz = SchwarzCoupling(experiment)
max_iters = 20
schwarz.run(max_iters)
```

In this setup, the simulation will be repeated 20 times with appropriate processing of the coupling data between two iterations.
The output will be placed in subsequently numbered directories in `output_dir` of the user context.
To make use of the runtime convergence criteria, `SchwarzCoupling.run()` accepts a keyword argument `stop_at_convergence` (defaults to `False`).
