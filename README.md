# Create_Wind_and_Solar_Resource_Files
A repository to collect the work of Caldeira Lab postdocs for generating wind and solar capacity factor files for using in MEM.

The code within is heavily based off of work done by Lei Duan: https://github.com/LDuan3008. Many thanks to him and Muriel Hauser
for preparing this code for uploading.


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



### Process MERRA-2 data into hourly and annual avg CFs

Files in: `/lustre/scratch/leiduan/MERRA2_data/`

Python scripts: `./get_{windCF, solarCF}.py`
Scripts that run the Python files and to submit: `./get_{wind,solar}_CF.csh`
Before running `.csh` scripts, change `python get_windCF.py YEAR` for your interested year. If no year is given, year-2016 will be calculated

#### Example processed data for 2016:

From `/lustre/scratch/leiduan/MERRA2_data/`:

Hourly wind and annual mean:
 * `MERRA2_400.tavg1_2d_slv_Nx.2016_wcf100m031225.nc`
 * `MERRA2_400.tavg1_2d_slv_Nx.2016_wcf100m031225_annual.nc`

Hourly solar and annual mean: 
 * `MERRA2_400.tavg1_2d_rad_Nx.2016_scf.nc`
 * `MERRA2_400.tavg1_2d_rad_Nx.2016_scf_annual.nc`

The `*_annual.nc` files contain the annual average capacity factor for each grid cell for each year 
and are approximately 1.5 MB, while the other files contain the full hourly time series 
information for each grid cell for each year and are approximately 7 GB.



### Resources

Create regional avg CFs:

 * First define the region interested (e.g., California)
 * Then find the shapefiles (end in `.shp`) for the interested region 
    * e.g., Download US states data from Natural Earth http://www.naturalearthdata.com/
 * Create a mask using shapefiles to match the resolution of the original CFs files
    * Tools can be used to deal with shapefiles for Python: shapely, Geopandas, or regionmask
    * See `example_create_mask_Africa.py` example below
 * Select grids that are within the interested region or use other criterions, and then calculate the average CFs for the interested region for each hour

Tools might be useful for Python:

 * Open and read NetCDF files:
    * NetCDF4, https://unidata.github.io/netcdf4-python/netCDF4/index.html
    * UV-CDAT, https://cdat.llnl.gov/
 * Plot spatial maps:
    * Cartopy (used with matplotlib), https://scitools.org.uk/cartopy/docs/latest/
    * VCS (used with UV-CDAT)



### Examples:

Example scripts can be found here: https://drive.google.com/drive/u/0/folders/1158yObOGB4O41nz74GISGQgmCGSXe1rk
 * Step0: calculate solar and wind from original MERRA-2 data, see:
    * `step0_get_windCF.py`
    * `step0_get_wind_CF.csh`
    * `step0_get_solarCF.py`
    * `step0_get_solar_CF.csh`
 * Step1: create masks for interested regions, see:
    * `step1p1_Create_masks_for_interested_regions.py`
    * `step1p2_Select_grids_for_interested_regions.py`
 * Step2: After you created the masks, apply them to the CFs data, see:
    * `step2_get_wind_time_series.py`
    * `step2_run_wind.csh`
    * `step2_get_solar_time_series.py`
    * `step2_run_solar.csh`
 * Step3: Convert the default NetCDF files from Step2 to csv, see:
    * `step3_generate_excel.py`
 * Data might need: some data you might need to use during calculations;

The above steps represent the complete process needed to generate the final time series of CFs;
For different purposes (e.g., different regions, different criterions) you might need to modify some of these scripts to better suit your purposes;
I did Step 1 and Step 3 on my Macbook, but you can modify it to run on MEMEX (you can write a `.csh` script to submit the job)



#### Useful geospatial packages for your CPU

You can install UC-CDAT as described on https://cdat.llnl.gov/. However, you might run 
into compatibility problems as UV-CDAT has not been updated in a while. 
Therefore, it is strongly suggested you follow this step-by-step description to install a lite 
version of UV-CDAT which only includes the few packages needed:
 * Step 1: install Anaconda
 * Step 2: Install UV-CDAT lite:
    * `>> conda create -n cdat_lite cdms2 cdutil -c conda-forge`
 * Step 3: install cartopy using the following command
    * `>> conda install -c conda-forge cartopy`
 * Step 4: install geopandas (which is pre-required by regionmask) using pip: 
    * `>> pip install geopandas`
 * Step 5: install the regionmask using pip:
    * `>> pip install regionmask`
 * Tyler tried all of these in one line and it is working thus far:
    * `>> conda create -n geo_stuff cdms2 cdutil cartopy geopandas regionmask -c conda-forge`
    * `>> conda activate geo_stuff`



### Creating CFs for a new region

What you need to do to get CF values for a new region

If all you want to do is to create new time series of CFs for a new region, you only 
have to go through Step1, Step2, and Step3 listed above. Don't worry about Step0. All you need from 
Step0 are its output files which are already in the Carnegie gDrive folder 
https://drive.google.com/drive/folders/1oiCxboncHBzS3WZcm0zdNRAwo1T6tZSg. 
The following steps explain in more detail what you need to do.

#### Step1: Create masks for the interested region

 * If you are looking into another region than the US you are likely not able to use the file «1.1-Create masks for interested regions.py» directly, but have to create your own mask
 * To do so, download the shapefiles of the region you are interested in (you can normally find them on google)
    * E.g. for Africa http://www.maplibrary.org/library/stacks/Africa/index.html
 * create a mask using regionmask. Follow the process described here: https://regionmask.readthedocs.io/en/stable/notebooks/create_own_regions.html
    * see example for Africa: `example_create_mask_Africa.py`
 * you should now be able to run `step1p2_Select_grids_for_interested_regions.py` with the mask you just created 

#### Step2: After you derive the masks

 * Run these files on Memex

#### Step3: post processing

 * You can run these files on your laptop again

