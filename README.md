# Create Wind and Solar Resource Files

A repository for generating wind and solar capacity factor files for use in energy system models.

## Installation and setup

We recommend using the conda package manager to install the required packages. If you do not have conda installed, you can download it [here](https://docs.conda.io/en/latest/miniconda.html).

1. Clone the repository to your local machine.
```git clone Create_Wind_and_Solar_Resource_Files```

2. cd into the repository.
```cd Create_Wind_and_Solar_Resource_Files```

3. Create a conda environment with the required packages and activate it.
```conda env create -f env.yml```
```conda activate capacity_factors_env```


## Converting climate variables into capacity factors

First, climate inputs (radiation, wind speed, temperature, etc) are converted to capacity factors at grid cell level with scripts in the `get_gridded_CF` directory (see `README.md` in that directory for more information). 

For the technical details of the calculations please see `Methodology.md`.


## Generating capacity factor input files for specific regions

Next, the capacity factor files are aggregated to the regions of interest with scripts in the `examples_ERA5` directory for ERA5 based capacity factors (see `README.md` in that directory for more information).

Similarly, region specific capacity factors based on MERRA-2 can be obtained by carrying out analogous steps in the `examples_MERRA2` directory. 
