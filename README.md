# Create_Wind_and_Solar_Resource_Files
A repository to collect the work of Caldeira Lab postdocs for generating wind and solar capacity factor files for using in MEM.

The code within is heavily based off of work done by Lei Duan: https://github.com/LDuan3008. Many thanks to him and Muriel Hauser for preparing this code for uploading.


## Methodology that converts climate variables into capacity factors

The Python codes that we used to convert climate inputs (radiation, wind speed, temperature, etc) to capacity factor at grid cell level are stored in the `get_gridded_CF` folder. 

For the technical details of the calculations please see `Methodology.md`.


## An example to generate capacity factor inputs 

We have two example folder here: 

`examples_MERRA2` includes codes and data that provide as an example to generate capacity factor input using MERRA-2. 

`examples_ERA5` includes codes and data that provide as an example to generate capacity factor input using ERA5. 

In the more recent works, we have swithed to ERA5 from MERRA-2, so here we focus on describing steps to generate the final input files used for ERA5. The whole process is similar for MERRA-2.

See `README.md` under `example_ERA5` for more infomration. 



Updated by Lei on Sep 22, 2023 