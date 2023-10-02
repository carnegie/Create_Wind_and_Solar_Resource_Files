# Create Wind and Solar Resource Files for the US (or other regions) based on gridded capacity factors

This directory includes the data and scripts that can be used to generate input capacity factor files based on ERA5 data. The same processes can be applied to examples in `example_MERRA2`. The selected region used as an example here is the US.

The capacity factors at each grid cell level which were created previously (see [README](https://github.com/carnegie/Create_Wind_and_Solar_Resource_Files/blob/master/README.md)) are now converted into capacity factors for specfic regions of interest. 

The following steps are used to select grid cells for the region of interest, average grid cells for those regions, and then convert the final outputs into a CSV table. 

### Generate US mask

Run the following script to generate US mask:

`python step1p1_Create_masks_for_interested_regions.py`

This will result in the NetCDF file `step1p1_selected_masks_US.nc` which indicate all grid cells within the US (excluding Alaska and Hawaii) at the ERA5 resolution. 

### Further select grids

The most straightforward approach is to simply average all grid cells in the US. However, there are several disadvantages with this approach. For example, the averaged capacity factor is lower than the actual resources one can get because grid cells with low-level resources are included. Also, the variability is smaller because there are more grid cells to smooth the hourly changes. Therefore, we provide three different ways for consideration:

Mthd1: average all grid cells within the US;
Mthd2: only consider grid cells that have a multi-year annual mean capacty factor above a certain threshold (can be changed in the code);
Mthd3: only consider the first X% (25% by default) grid cells that have the largest multi-year annual mean capacty factors within the region. 

By default, we use Mthd3 for our latest studies. To do this, run the following Python script:

`python step1p2_Select_grids_for_interested_regions.py`

This will lead to the NetCDF file `step1p2_selected_USmask_outfile_ERA5.nc` which indicate all grid cells that are further selected. 

### Average grid cells

To average all grid cells selected, run the script `step2_get_time_series_newERA5.py`. 
Modify the path to the grid-scale capacity factor data in this script to point where you stored these.
Then run the script with the following command including the specifics as arguments:

`python step2_get_time_series_newERA5.py 2016 REGION METHOD TODAYS_DATE SCF_WCF SOURCE MASK` 

for example:

`python step2_get_time_series_newERA5.py 2016 US 3 20230925 scf ERA5 ERA5` 


This step involves reading the grid-cell scale capacity factor files which are large in size. So it is recommanded to run this on a cluster. 

### Convert the output *.nc files to CSV 

The previous step will generate a list of NetCDF files, each contains the hourly average capacity factor for a year. To convert it to CSV table as recognized by many models, run the following script, providing the target output directory as an argument:

`python step3_generate_excel.py PATH_TO_NETCDF`

for example:

`python step3_generate_excel.py outfiles/20230922_US_mthd3`
