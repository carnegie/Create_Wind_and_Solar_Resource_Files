import numpy as np
import xarray as xr

log_file = open('log_file', 'a')
log_file.write('Getting solar and wind CFs time series...\n')
log_file.close()

data_path = '/lustre/scratch/leiduan/MERRA2_data/MERRA2_CF_Data/'

def get_prefix_name_solar(year):
    if year <= 1991:
        prefix_name = "MERRA2_100.tavg1_2d_rad_Nx."
    if year > 1991 and year <= 2000:
        prefix_name = "MERRA2_200.tavg1_2d_rad_Nx."
    if year > 2000 and year <= 2010:
        prefix_name = "MERRA2_300.tavg1_2d_rad_Nx."
    if year > 2010:
        prefix_name = "MERRA2_400.tavg1_2d_rad_Nx."
    return prefix_name

def get_prefix_name_wind(year):
    if year <= 1991:
        prefix_name = "MERRA2_100.tavg1_2d_slv_Nx."
    if year > 1991 and year <= 2000:
        prefix_name = "MERRA2_200.tavg1_2d_slv_Nx."
    if year > 2000 and year <= 2010:
        prefix_name = "MERRA2_300.tavg1_2d_slv_Nx."
    if year > 2010:
        prefix_name = "MERRA2_400.tavg1_2d_slv_Nx."
    return prefix_name

### Step 0 ###
## Get lat/lon info

# f_axis = xr.open_dataset(data_path+'data/SWGDN.nc')
f_axis = xr.open_dataset('data/SWGDN.nc')
lon = np.array(f_axis.lon)
lat = np.array(f_axis.lat)
bounds_lon = np.array(f_axis.bounds_lon)
bounds_lat = np.array(f_axis.bounds_lat)
del f_axis

log_file = open('log_file', 'a')
log_file.write('Latitude and longitude coordinates read\n')
log_file.close()

### Step 1 ###
## Read the grid cells of the region of interest

# f_region = xr.open_dataset(data_path+'data/region_of_interest.nc')
f_region = xr.open_dataset('data/region_of_interest.nc')
solar_CF_of_interest = np.array(f_region.solar_CF_of_interest)
wind_CF_of_interest = np.array(f_region.wind_CF_of_interest)
del f_region

log_file = open('log_file', 'a')
log_file.write('Gridpoints of region of interest read\n')
log_file.close()

### Step 2 ###
## Calculate the area of each cell defined by the lat/lon grid
# https://www.pmel.noaa.gov/maillists/tmap/ferret_users/fu_2004/msg00023.
# https://en.wikipedia.org/wiki/Spherical_sector

R_earth = 6.371*10**6
cell_areas = np.zeros((len(lat),len(lon)))
for ii in range(len(lat)):
    for jj in range(len(lon)):
        cell_areas[ii,jj] = 2*np.pi*R_earth**2*np.absolute(np.sin(bounds_lat[ii,1]*np.pi/180)-np.sin(bounds_lat[ii,0]*np.pi/180))*np.absolute(bounds_lon[jj,1]-bounds_lon[jj,0])/360

log_file = open('log_file', 'a')
log_file.write('Cell areas calculated\n')
log_file.close()

### Step 3 ###
## Calculate hourly solar/wind CFs time series and save them in a csv file

start_year = 1980
n_years = 1 
for kk in range(n_years):
    year = start_year+kk

    # Get dates and number of hours

    dates = np.arange(str(year), str(year+1), dtype='datetime64[h]')
    time = np.array([t.item() for t in dates])
    timesteps = len(time)
    time_c = np.zeros((timesteps,4))
    for tt in range(timesteps):
        time_c[tt] = np.array([time[tt].year,time[tt].month,time[tt].day,time[tt].hour])

    # Get solar/wind CFs

    # solar_data = xr.open_dataset(data_path+'MERRA2_%d_solar_CF.nc'%(year))
    # wind_data = xr.open_dataset(data_path+'MERRA2_%d_wind_CF.nc'%(year))
    solar_data = xr.open_dataset(data_path+get_prefix_name_solar(year)+'%d_scf.nc'%(year))
    wind_data = xr.open_dataset(data_path+get_prefix_name_wind(year)+'%d_wcf100m031225.nc'%(year))
    solar_CF = np.array(solar_data.scf)
    wind_CF = np.array(wind_data.wcf)
    del solar_data, wind_data

    # Calculate hourly average solar/wind CFs

    aggregated_resources = False
    if (aggregated_resources):
        hourly_average_solar_CF_of_interest = np.zeros(timesteps)
        hourly_average_wind_CF_of_interest = np.zeros(timesteps)
        for tt in range(timesteps):
            hourly_average_solar_CF_of_interest[tt] = np.nansum(cell_areas*solar_CF[tt]*solar_CF_of_interest)/np.nansum(cell_areas*solar_CF_of_interest)
            if np.isnan(hourly_average_solar_CF_of_interest[tt]):
                hourly_average_solar_CF_of_interest[tt] = 0
            hourly_average_wind_CF_of_interest[tt] = np.nansum(cell_areas*wind_CF[tt]*wind_CF_of_interest)/np.nansum(cell_areas*wind_CF_of_interest)
            if np.isnan(hourly_average_wind_CF_of_interest[tt]):
                hourly_average_wind_CF_of_interest[tt] = 0
        solar_time_series = np.c_[time_c,hourly_average_solar_CF_of_interest]
        wind_time_series = np.c_[time_c,hourly_average_wind_CF_of_interest]
        f_solar = open('Solar_time_series.csv','a')
        np.savetxt(f_solar,solar_time_series,fmt="%s",delimiter=",")
        f_solar.close()
        f_wind = open('Wind_time_series.csv','a')
        np.savetxt(f_wind,wind_time_series,fmt="%s",delimiter=",")
        f_wind.close()
    else:
        hourly_solar_CF_of_interest = np.zeros((timesteps,len(lat),len(lon)))
        hourly_wind_CF_of_interest = np.zeros((timesteps,len(lat),len(lon)))
        for tt in range(timesteps):
            hourly_solar_CF_of_interest[tt] = solar_CF[tt]*solar_CF_of_interest
            hourly_wind_CF_of_interest[tt] = wind_CF[tt]*wind_CF_of_interest
        for ii in range(len(lat)):
            for jj in range(len(lon)):
                if (~np.isnan(solar_CF_of_interest[ii,jj])):
                    solar_time_series = np.c_[time_c,hourly_solar_CF_of_interest[:,ii,jj]]
                    f_solar = open('Solar_time_series_at_Lat_%6.3f_Lon_%6.3f.csv'%(lat[ii],lon[jj]),'a')
                    np.savetxt(f_solar,solar_time_series,fmt="%s",delimiter=",")
                    f_solar.close()
                if (~np.isnan(wind_CF_of_interest[ii,jj])):
                    wind_time_series = np.c_[time_c,hourly_wind_CF_of_interest[:,ii,jj]]
                    f_wind = open('Wind_time_series_at_Lat_%6.3f_Lon_%6.3f.csv'%(lat[ii],lon[jj]),'a')
                    np.savetxt(f_wind,wind_time_series,fmt="%s",delimiter=",")
                    f_wind.close()

    log_file = open('log_file', 'a')
    log_file.write('Hourly solar/wind CFs time series calculated for year %d\n'%(year))
    log_file.close()
