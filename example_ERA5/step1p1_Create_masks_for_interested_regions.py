import cdms2 as cdms
import numpy as np
import MV2 as MV
import geopandas as gpd, regionmask

# ------------------------------------------------------------------------
# # When using MERRA2:
# f_axis = cdms.open('data/SWGDN.nc')
# v=f_axis('SWGDN')
# lat=v.getAxis(1)  # latitude
# lon=v.getAxis(2)  # longitude
# f_axis.close()
# output_file_name = 'selected_CtyMasks_MERRA2.nc'

# f_land_mask = cdms.open('data/land_sea_mask_merra.nc4')
# land_mask_tmp = f_land_mask('FRLAND',squeeze=1)
# land_mask_tmp[land_mask_tmp>=0.5] = 1.
# land_mask_tmp[land_mask_tmp<0.5]  = 0.
# land_mask = MV.array(MV.masked_equal(land_mask_tmp,0.))
# land_mask.setAxis(0,lat);      land_mask.setAxis(1,lon)
# f_land_mask.close()


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




"""
# Plot and see
import matplotlib.pyplot as plt 
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors as colors
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.path as mpath

# g=cdms.open('step1p1_selected_masks_US.nc')
# a = g('mask_US', squeeze=1)
# g.close() 

g=cdms.open('step1p2_selected_USmask_outfile_ERA5.nc')
a = g('smask_US_mthd1', squeeze=1)
g.close() 

print (a)
print (a.min())
print (a.max())

ax1 = plt.subplot(111, projection=ccrs.PlateCarree())
ax1.add_feature(cfeature.COASTLINE)
# ax1.add_feature(cfeature.BORDERS)
# ax1.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())
ax1.add_feature(cfeature.STATES); ax1.set_extent([-150, -60, 20, 60], crs=ccrs.PlateCarree()); name = 'US_scale'
mp = ax1.pcolor(lon, lat, a, cmap='Greens', norm=colors.Normalize(vmin=0, vmax=1), transform=ccrs.PlateCarree())
plt.colorbar(mp, ax=ax1, extend='max', shrink=0.5, orientation='vertical')
plt.show()
plt.clf()
# """