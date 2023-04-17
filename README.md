# EC-Earth SCM Tools

This repository contains helpful scripts to run the EC-Earth AOSCM and analyze its output.
The assumption is that the AOSCM is compiled on your system, as described in the documentation.

Particularly:
- the Python wrapper `SchwarzCoupling` allows to do Schwarz Waveform Relaxation with the AOSCM
- experiments can be configured and executed directly from Python (using `utils/templates.py` and the `AOSCM` class in `utils/helpers.py`, respectively)
- `user_context.py` contains your local environment, in order to find executables, input data and output files

## Requirements

The scripts use Python 3.9 as a basis. The following external packages are required:

For configuring/running the AOSCM:
- [Jinja](https://jinja.palletsprojects.com/en/3.1.x/)
- [NumPy](numpy.org)
- [pandas](https://pandas.pydata.org/)
- [ruamel.yaml](https://pypi.org/project/ruamel.yaml/)
- [xarray](https://docs.xarray.dev/en/stable/)

For plotting:
- [ProPlot](https://proplot.readthedocs.io/en/stable/)

## Usage

Tutorials:

1. Configure and run a single experiment
2. Change the coupling algorithm (parallel/atmosphere-first/ocean-first)
3. Run a Schwarz Waveform Relaxation simulation
4. Generate a valid `rstas.nc` file for OASIS initialization
5. Run an ensemble simulation
6. Visualize output