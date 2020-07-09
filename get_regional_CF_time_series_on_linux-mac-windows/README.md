### These scripts are used to create regional avg CFs:


(These scripts were created by Lei and Enrico modified them to run on Windows also) 

 * First define the region interested (e.g., CONUS)
 * Select grid cells that are within the region of interest
 * Further filter the cells based on user-defined criteria
 * Calculate either area-weighted average hourly CFs for the region of interest or hourly CFs for each cell of the region of interest


#### Scripts:

 * Step1: create masks for region of interest, see:
    * `step1_Create_masks_for_region_of_interest.py`
 * Step2: After you created the masks, apply them to the CFs data and generate the csv result file, see:
    * `step2_get_solar_and_wind_time_series.py`


#### Packages required run these scripts

 * The only python packages required to run these scripts are `xarray`, which is already available on MEMEX or can be easily installed on any OS, and `regionmask`, which can also be easily installed through conda on any OS.

    * `>> conda install xarray regionmask`


### Creating CFs for a new region

To obtain CF values for a new region, you have to modify Step1. The output file for the new region of interest must include an array where you have 1s for the grid cells belonging to the region and np.nan elsewhere. 

After creating a new region_of_interest.nc file, you can run Step2 in batch mode, through step2_run_solar_and_wind_time_series.sh.

