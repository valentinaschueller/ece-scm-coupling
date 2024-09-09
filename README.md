# EC-Earth SCM Tools

This repository contains helpful scripts to run the EC-Earth AOSCM, with a focus on switching coupling algorithms at runtime.
Ultimately, the package allows to set up and run AOSCM simulations completely from Python.

It is required that the AOSCM is compiled on your system, as described in the documentation.
You can install the package by cloning the code and running

```bash
> pip install .
```

inside the top-level directory.

Particularly:
- experiments can be configured and run directly from Python (using `utils/templates.py` and the `AOSCM` class in `utils/helpers.py`, respectively)
- the Python wrapper `SchwarzCoupling` allows to do Schwarz Waveform Relaxation with the AOSCM
- `context.py` allows to set your local environment, in order to find the correct executables, input data, and output files

## Usage

Before using the package, make sure to:

1. Have an installed version of the AOSCM on your system, along with initial/forcing files for your experiment(s).
2. Install the package in your environment, as described above.

Tutorials:

1. Configure and run a single experiment
2. Run a Schwarz Waveform Relaxation simulation
