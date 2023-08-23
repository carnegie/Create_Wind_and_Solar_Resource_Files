### These scripts are used to process MERRA-2 data into hourly and annual global CFs


The hourly and annual global CFs need to be created only once and are already available in the Carnegie Google Drive folder.


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


Files in: `/lustre/scratch/leiduan/MERRA2_data/`

Python scripts: `./get_{windCF, solarCF}.py`
Scripts that run the Python files and to submit: `./get_{wind,solar}_CF.csh`
Before running `.csh` scripts, change `python get_windCF.py YEAR` for your interested year. If no year is given, year-2016 will be calculated


#### Scripts:

Example scripts can be found here: https://drive.google.com/drive/u/0/folders/1158yObOGB4O41nz74GISGQgmCGSXe1rk

 * Step0: calculate solar and wind from original MERRA-2 data, see:
    * `step0_get_windCF.py`
    * `step0_get_wind_CF.csh`
    * `step0_get_solarCF.py`
    * `step0_get_solar_CF.csh`


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
    * `>> conda create -n geo_stuff cdms2 cdutil cartopy geopandas regionmask descartes -c conda-forge`
    * `>> conda activate geo_stuff`
