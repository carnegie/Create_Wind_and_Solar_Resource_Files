# Title

This folder includes the entire steps that are needed to generate the final hourly capacity factor input data for energy system models.

An example to generate the US input is used. 


# Codes

### Step 1, generate US mask

Since the ERA5 database provides grid scale climate data, and our pre-process codes in `get_gridded_CF` convert these climate data into capacity factor at the same grid scale level, the first step we need to do is to find all grid cells that belong to the region of interests. 

To do this, I am relying on the Python package regionmask (https://regionmask.readthedocs.io/en/stable/#). Regionmask provides many convenient ways to create masks at country, county, scientific region, etc. scale levels. Regionmask can also be combined with Polygon or Shapfile to easily create masks. 

To generate US mask, run python script: 

`python step1p1_Create_masks_for_interested_regions.py`

This script will generate a NetCDF file, `step1p1_selected_masks_US.nc`, including the mask variable of US. 


### Step 2, select grids using different approaches

After selecting the US grid cell, the simplest way is to average capacity factor across all these grids. In addition to this, we can also select a subset of grid cells. We have develop a code that contrains three ways to select grid cells:

(1) Only remove grid cells that are mostly water but keep all land grids;
(2) Remove grid cells that are mostly water, and then only select land grid cells that have an multi-year annyal mean capacity factor above X (X can be changed);
(3) Remove grid cells that are mostly water, and then only select the top X fraction (0.25 by default) grid cells that have the largest multi-year annyal mean capacity factor.

To do this, run python script:

`python step1p2_Select_grids_for_interested_regions.py`

By default, this will result a new NetCDF file named step1p2_selected_USmask_outfile_ERA5.nc here that include all these three types denoted as mthd1, mthd2, and mthd3.


### Step 3, calculated average hourly capacity factor 

Once you have selected grid mask, you can then run step2 code, which:

(1) Take the global-scale capacity factor file and select grid cells of interests;
(2) Average these grid cells using grid area as weights;
(3) Output a series of NetCDF files that contain hourly mean capacity factor of a certain year. 

To do this, run python script:

`python step2_get_time_series_newERA5.py`

Note that because this step requires to read a bunch of files that are large in size, it is recommand to run this step on a HPC. 

### Step 4, convert the output NetCDF to csv input 

To do this, run the step3 python script:

`python step3_generate_excel.py FOLDER_LOCATION_OF_CAPACITY_FACTOR`

`FOLDER_LOCATION_OF_CAPACITY_FACTOR` is the folder where NetCDF outputs from step3 are stored. 