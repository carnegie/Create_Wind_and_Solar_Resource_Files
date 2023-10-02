import numpy as np
import regionmask
import xarray as xr

### Step 0 
## Read the variable "SWGDN" from "SWGDN.nc" to get lat/lon info

f_axis = xr.open_dataset('data/SWGDN.nc')
lon = np.array(f_axis.lon)
lat = np.array(f_axis.lat)
del f_axis

### Step 1
## Isolate land from ocean grid points 
# Identify grid points with "FRLAND" >= 0.5 as land and set a value of 1
# Define other grid points ("FRLAND" < 0.5) as ocean and set NaN

f_land = xr.open_dataset('data/land_sea_mask_merra.nc4')
land_area = np.array(f_land.FRLAND[0]) # land fraction
land_area[land_area>=0.5] = 1
land_area[land_area<0.5] = np.nan
del f_land

### Step 2
## Identify the region of interest -- This part can be modifies as needed
# Populate the array "region_of_interest" with NaN/1 where 1s identify the gridpoints of your region of interest

region_of_interest = np.zeros((len(lat),len(lon)))
states = regionmask.defined_regions.natural_earth.us_states_50
mask = np.array(states.mask(lon, lat, wrap_lon=False))
states_ids_of_interest = np.concatenate((np.arange(1, 11),np.arange(12, 51))) # CONUS
# states_ids_of_interest = np.array([34]) # New York
# states_ids_of_interest = np.array([43]) # Texas
for i in range(len(states_ids_of_interest)):
    region_of_interest[mask==states_ids_of_interest[i]] = 1
del states, mask, states_ids_of_interest, i
region_of_interest[region_of_interest<0.5] = np.nan
region_of_interest = region_of_interest*land_area

### Step 3 ###
## Calculate the decadal mean global CFs between 2009 and 2018

start_year_decadal = 2009
n_years_decadal = 10
solar_CF_decadal = np.zeros((len(lat),len(lon)))
wind_CF_decadal = np.zeros((len(lat),len(lon)))
for kk in range(n_years_decadal):
    year = start_year_decadal+kk
    solar_data = xr.open_dataset('data/MERRA2_%d_solar_CF_annual.nc'%(year))
    wind_data = xr.open_dataset('data/MERRA2_%d_wind_CF_annual.nc'%(year))
    solar_CF_decadal = solar_CF_decadal + np.array(solar_data.scf_annual)/10
    wind_CF_decadal = wind_CF_decadal + np.array(wind_data.wcf_annual)/10
del solar_data, wind_data, kk, year, n_years_decadal, start_year_decadal

### Step 4 ###
## Further filter grid cells based on different purposes
# idx == 1: use all grid cells of the region of interest
# idx == 2: set thresholds for wind and solar separately, and filter values lower than that
# idx == 3: take grid cells with top X% amount of wind and solar for the region of interest

idx = 1
if idx == 1:
    solar_CF_of_interest = region_of_interest
    wind_CF_of_interest = region_of_interest
elif idx == 2:
    solar_threshold = 0.26
    wind_threshold = 0.26
    solar_CF_subset = np.zeros((len(lat),len(lon)))
    wind_CF_subset = np.zeros((len(lat),len(lon)))
    solar_CF_subset[solar_CF_decadal>=solar_threshold] = 1
    solar_CF_subset[solar_CF_decadal<solar_threshold] = np.nan
    wind_CF_subset[wind_CF_decadal>=wind_threshold] = 1
    wind_CF_subset[wind_CF_decadal<wind_threshold] = np.nan
    solar_CF_of_interest = solar_CF_subset*region_of_interest
    wind_CF_of_interest = wind_CF_subset*region_of_interest
elif idx == 3:
    solar_top_percentage = 0.25
    wind_top_percentage = 0.25
    solar_sorted = np.sort(solar_CF_decadal[~np.isnan(solar_CF_decadal*region_of_interest)],axis=None)
    wind_sorted = np.sort(wind_CF_decadal[~np.isnan(wind_CF_decadal*region_of_interest)],axis=None)
    solar_threshold = solar_sorted[int(len(solar_sorted)*(1-solar_top_percentage))]
    wind_threshold = wind_sorted[int(len(wind_sorted)*(1-wind_top_percentage))]
    solar_CF_subset = np.zeros((len(lat),len(lon)))
    wind_CF_subset = np.zeros((len(lat),len(lon)))
    solar_CF_subset[solar_CF_decadal>=solar_threshold] = 1
    solar_CF_subset[solar_CF_decadal<solar_threshold] = np.nan
    wind_CF_subset[wind_CF_decadal>=wind_threshold] = 1
    wind_CF_subset[wind_CF_decadal<wind_threshold] = np.nan
    solar_CF_of_interest = solar_CF_subset*region_of_interest
    wind_CF_of_interest = wind_CF_subset*region_of_interest
# average_solar_CF_of_interest = np.nansum(cell_areas*solar_CF_decadal*solar_CF_of_interest)/np.nansum(cell_areas*solar_CF_of_interest)
# average_wind_CF_of_interest = np.nansum(cell_areas*wind_CF_decadal*wind_CF_of_interest)/np.nansum(cell_areas*wind_CF_of_interest)
# if np.isnan(average_solar_CF_of_interest):
#     average_solar_CF_of_interest = 0
# if np.isnan(average_wind_CF_of_interest):
#     average_wind_CF_of_interest = 0
# print ("Averaged solar capacity factor for the filtered grids is: ", average_solar_CF_of_interest)
# print ("Averaged wind capacity factor for the filtered grids is: ", average_wind_CF_of_interest)

### Step 5
## Save the filtered region of interest

region_of_interest_out = xr.Dataset({'solar_CF_of_interest':(('lat', 'lon'),solar_CF_of_interest),'wind_CF_of_interest':(('lat', 'lon'),wind_CF_of_interest)},coords={'lat':lat,'lon':lon})
region_of_interest_out.to_netcdf('data/region_of_interest.nc')
