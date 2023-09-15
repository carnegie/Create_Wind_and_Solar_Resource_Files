import cdms2 as cdms, numpy as np, MV2 as MV, geopandas as gpd, regionmask
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
import pandas as pd

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
from matplotlib import pyplot as plt


### Get land mask and lat/lon info
f_land_mask = cdms.open('./example/ERA5_landsea_mask.nc')
lsm = f_land_mask('lsm', squeeze=1)[0]
f_land_mask.close() 

lat = lsm.getAxis(0)
lon = lsm.getAxis(1)

lsm[lsm>0.5] = 1.
lsm[lsm<=0.5]  = 0.

land_mask = MV.array(MV.masked_equal(lsm, 0.))
land_mask.setAxis(0,lat)
land_mask.setAxis(1,lon)


### Create country mask 
# countries = regionmask.defined_regions.natural_earth_v5_0_0.countries_110
countries = regionmask.defined_regions.natural_earth_v4_1_0.countries_110
mask = np.array(countries.mask(lon, lat, wrap_lon=True))
name = countries.names


### Create US mask
# Exclude Alaska and Hawaii from the US mask 
longitudes, latitudes = np.meshgrid(lon, lat)
# Alaska
alaska_lat_mask = (latitudes >= 51) & (latitudes <= 71)
# alaska_lon_mask = (longitudes >= 188) & (longitudes <= 230)
alaska_lon_mask = (longitudes >= 188) & (longitudes <= 224)
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

# print ()
# print ()
# print (np.sum(US_mask * land_mask))
# # stop 

### Create a new NetCDF file and save the mask
g=cdms.open('./example/selected_masks_US.nc','w')
g.write(US_mask)
g.close() 


# ### Plot the mask 
# ax = plt.subplot(111, projection = ccrs.PlateCarree())
# ax.set_global()
# ax.add_feature(cfeature.COASTLINE)
# ax.add_feature(cfeature.STATES)
# ax.pcolormesh( lon, lat, US_mask * land_mask, transform=ccrs.PlateCarree() )
# ax.set_extent([-180,-50, 10, 40])
# plt.show()
# plt.clf() 