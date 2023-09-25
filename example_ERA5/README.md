# Description 

This repository includes the data and scripts that can be used to generate input capacity factor files for the US based on ERA5 data. The same processes can be applied to examples in `example_MERRA2`. 

The capacity factors at each grid cell level which were created previously (see [README](https://github.com/carnegie/Create_Wind_and_Solar_Resource_Files/blob/master/README.md)) are now converted into capacity factors for specfic regions of interest. 

The following steps are used to select grid cells for the region of interest, average grid cells for those regions, and then convert the final outputs into a CSV table. 

### Generate US mask

Run the following script to generate US mask:

`python step1p1_Create_masks_for_interested_regions.py `

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

To average all grid cells selected, run the following script:

`python step2_get_time_series_newERA5.py` 

In order to do this correct, you need to modify the example script by telling the model where the grid-scale capacity factor data is, and which mask file/region you are using. 

This step involves reading the grid-cell scale capacity factor files which are large in size. So it is recommanded to run this on a cluster. 

### Convert the output *.nc files to CSV 

The previous step will generate a list of NetCDF files, each contrains the hourly average capacity factor for a year. To convert it to CSV table as recognized by the model, run the following script:

`python step3_generate_excel.py PATH_TO_NETCDF`
