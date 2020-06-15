# Create_Wind_and_Solar_Resource_Files
A repository to collect the work of Caldeira Lab postdocs for generating wind and solar capacity factor files for using in MEM.



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
Hourly wind and annual mean:
 * `../MERRA2_400.tavg1_2d_slv_Nx.2016_wcf100m031225.nc`
 * `../MERRA2_400.tavg1_2d_slv_Nx.2016_wcf100m031225_annual.nc`
Hourly solar and annual mean: 
 * `../MERRA2_400.tavg1_2d_rad_Nx.2016_scf.nc`
 * `../MERRA2_400.tavg1_2d_rad_Nx.2016_scf_annual.nc`
 * `*_annual.nc` contains the annual average capacity factor for each grid cell



### Resources

Create regional avg CFs:

 * First define the region interested (e.g., California)
 * Then find the shapefiles (end in `.shp`) for the interested region 
    * e.g., Download US states data from Natural Earth http://www.naturalearthdata.com/
 * Create a mask using shapefiles to match the resolution of the original CFs files
    * Tools can be used to deal with shapefiles for Python: shapely, Geopandas, or regionmask
    * See examples below
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
 * Step0: calculate solar and wind from original MERRA-2 data;
 * Step1: create masks for interested regions
 * Step2: After you created the masks, apply them to the CFs data
 * Step3: Convert the default NetCDF files from Step2 to csv
 * Data might need: some data you might need to use during calculations;

The above steps represent the complete process needed to generate the final time series of CFs;
For different purposes (e.g., different regions, different criterions) you might need to modify some of these scripts to better suit your purposes;
I did Step 1 and Step 3 on my Macbook, but you can modify it to run on MEMEX (you can write a `.csh` script to submit the job)

