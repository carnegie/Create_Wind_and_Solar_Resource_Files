import numpy as np
import geopandas as gpd, regionmask
import cdms2 as cdms
import MV2 as MV


# When using ERA5:
fmask = cdms.open('data/ERA5_landsea_mask.nc')
land_mask_tmp = fmask('lsm', squeeze=1)[0]
lat = land_mask_tmp.getAxis(0)
lon = land_mask_tmp.getAxis(1)
fmask.close()

land_mask_tmp[land_mask_tmp>=0.5] = 1.
land_mask_tmp[land_mask_tmp<0.5]  = 0.
land_mask = MV.array(MV.masked_equal(land_mask_tmp,0.))
land_mask.setAxis(0,lat);      land_mask.setAxis(1,lon)
output_file_name = 'selected_CtyMasks_ERA5.nc'



# ------------------------------------------------------------------------
# """
# Get US masks
countries = regionmask.defined_regions.natural_earth_v5_0_0.countries_110
mask = np.array(countries.mask(lon, lat, wrap_lon=True))
name = countries.names

### Create US mask
# Exclude Alaska and Hawaii from the US mask 
longitudes, latitudes = np.meshgrid(lon, lat)
# Alaska
alaska_lat_mask = (latitudes >= 51) & (latitudes <= 71)
alaska_lon_mask = (longitudes >= 188) & (longitudes <= 230)
alaska_combined_mask = alaska_lat_mask & alaska_lon_mask
# Hawaii
hawaii_lat_mask = (latitudes >= 18.5) & (latitudes <= 20.5)
hawaii_lon_mask = (longitudes >= 204) & (longitudes <= 206)
hawaii_combined_mask = hawaii_lat_mask & hawaii_lon_mask
# Combine the Masks
final_combined_mask = alaska_combined_mask | hawaii_combined_mask
# Separate US mask 
mask[mask!=4] = -9999
mask[final_combined_mask==True] = -9999
mask_masked = np.ma.masked_equal(mask, -9999) * 0 + 1

US_mask = MV.array(mask_masked)
US_mask.setAxis(0,lat)
US_mask.setAxis(1,lon)
US_mask.id='mask_US'

### Create a new NetCDF file and save the mask
g=cdms.open('step1p1_selected_masks_US.nc','w')
g.write(US_mask)
g.close() 
# """

