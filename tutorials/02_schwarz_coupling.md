# Schwarz Waveform Relaxation with the EC-Earth AOSCM

Schwarz waveform relaxation (SWR) is taken care of by the class `SchwarzCoupling` in the module `schwarz_coupling.py`.
Prerequisites before you can run an SWR experiment:
- The EC-Earth AOSCM is already compiled on your system.
- You have already created the `Context` for your system and the `Experiment` parameters
- The runscript directory (`context.runscript_dir`) contains scripts for a regular coupled run *and* the Schwarz correction.

The first two bullet points can be checked by running a basic AOSCM experiment, as described in the [respective tutorial](01_basic_aoscm_experiment.md).
A minimal Python script for an SWR simulation looks as follows:

```python
from AOSCMcoupling.schwarz_coupling import SchwarzCoupling

schwarz = SchwarzCoupling(experiment, context)
max_iters = 20
schwarz.run(max_iters)
```

In this setup, the simulation will be repeated 20 times with appropriate processing of the coupling data between two iterations.
The output will be placed in subsequently numbered directories in `output_dir` of the user context.
To make use of the runtime convergence criteria, `SchwarzCoupling.run()` accepts a keyword argument `stop_at_convergence` (defaults to `False`).
