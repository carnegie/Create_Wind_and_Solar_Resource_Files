# Create_Wind_and_Solar_Resource_Files
A repository to collect the work of Caldeira Lab postdocs for generating wind and solar capacity factor files for using in MEM.

The code within is heavily based off of work done by Lei Duan: https://github.com/LDuan3008. Many thanks to him and Muriel Hauser
for preparing this code for uploading.

## Resources
Lei created a screen cast showing how to use the step1 and step2 scripts in the `get_regional_CF_time_series_on_linux-mac` directory: https://drive.google.com/file/d/13_TprW7_wJt0_rK0skIyIdh33s1jwpBp/view?usp=sharing


## Methodology

For the technical details of the calculations please see `Methodology.md`.


## MERRA-2 Solar and Wind CFs

We are using MERRA-2 reanalysis data: see https://gmao.gsfc.nasa.gov/reanalysis/MERRA-2/ and recommended citation: https://doi.org/10.1175/JCLI-D-16-0758.1


### Original MERRA-2 data

https://daac.gsfc.nasa.gov/datasets?page=1&project=MERRA-2 

Lei will periodically pull the newest data from MERRA-2 down to the Memex cluster. If this has not been done for a while, please send a request to get the latest data if needed.


#### To downloaded data on MEMEX:

See these files:
 * Wind:  `/lustre/scratch/leiduan/MERRA2_data/Wind`
 * Solar: `/lustre/scratch/leiduan/MERRA2_data/Solar`

Download scripts example by Lei: 
 * Input file: `/lustre/scratch/leiduan/MERRA2_data/Wind/wind_list3.txt`
 * Script: `/lustre/scratch/leiduan/MERRA2_data/Wind/test.csh`


### Scripts:

Example scripts can be found here: https://drive.google.com/drive/u/0/folders/1158yObOGB4O41nz74GISGQgmCGSXe1rk

 * Calculate solar and wind from original MERRA-2 data, see files in get_global_CF_time_series.
 * Create masks for interested regions, apply them to the CFs data, save the results to csv files, see files in get_regional_CF_time_series.
 * Data might need: some data you might need to use during calculations.

The above steps represent the complete process needed to generate the final time series of CFs.
For different purposes (e.g., different regions, different criterions) you might need to modify some of these scripts to better suit your purposes.
