

import cdms2 as cdms, MV2 as MV, cdutil 
import numpy as np 


def removenan(var):
    whereisnan = np.isnan(var)
    var_out = np.ma.masked_where(whereisnan, var) * 0 + 1
    return var_out



### Step 0, prepare
### Get land mask and lat/lon info
f_land_mask = cdms.open('./example/ERA5_landsea_mask.nc')
lsm = f_land_mask('lsm', squeeze=1)[0]
f_land_mask.close() 
lat = lsm.getAxis(0)
lon = lsm.getAxis(1)
lsm[lsm>=0.5] = 1.
lsm[lsm<0.5]  = 0.
land_mask = MV.array(MV.masked_equal(lsm, 0.))
land_mask.setAxis(0,lat)
land_mask.setAxis(1,lon)

####
com1 = './example/selected_USmask_outfile_ERA5.nc'
com2 = './example/cc_selected_USmask_outfile_ERA5.nc'

f1 = cdms.open(com1)
f2 = cdms.open(com2)

f1_smask_US_mthd1 = removenan(f1('smask_US_mthd1'))
f2_smask_US_mthd1 = removenan(f2('smask_US_mthd1'))

# f1_smask_US_mthd2 = removenan(f1('smask_US_mthd2'))
# f2_smask_US_mthd2 = removenan(f2('smask_US_mthd2'))

# f1_smask_US_mthd3 = removenan(f1('smask_US_mthd3'))
# f2_smask_US_mthd3 = removenan(f2('smask_US_mthd3'))

# f1_wmask_US_mthd1 = removenan(f1('wmask_US_mthd1'))
# f2_wmask_US_mthd1 = removenan(f2('wmask_US_mthd1'))

# f1_wmask_US_mthd2 = removenan(f1('wmask_US_mthd2'))
# f2_wmask_US_mthd2 = removenan(f2('wmask_US_mthd2'))

# f1_wmask_US_mthd3 = removenan(f1('wmask_US_mthd3'))
# f2_wmask_US_mthd3 = removenan(f2('wmask_US_mthd3'))

f1.close() 
f2.close()


print () 
print () 
print (f1_smask_US_mthd1)
print (f2_smask_US_mthd1) 
print ()
print (f1_smask_US_mthd1.max(), f1_smask_US_mthd1.min())
print (f2_smask_US_mthd1.max(), f2_smask_US_mthd1.min())
print () 
print (np.sum(f1_smask_US_mthd1))
print (np.sum(f2_smask_US_mthd1))

### Plot

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


def plot_region(lon, lat, mask_region, extent=[-150,-50, 10, 80]):
    ax = plt.subplot(111, projection = ccrs.PlateCarree())
    ax.set_global()
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.STATES)
    im = ax.pcolormesh( lon, lat, mask_region, transform=ccrs.PlateCarree() )
    ax.set_extent(extent)
    plt.show() 
    plt.clf() 

plot_region(lon, lat, f1_smask_US_mthd1, extent=[-180,-50, 10, 40])
plot_region(lon, lat, f2_smask_US_mthd1, extent=[-180,-50, 10, 40])

# diff = np.ma.masked_equal(np.ma.filled(f1_smask_US_mthd1, 0) - np.ma.filled(f2_smask_US_mthd1, 0), 0)
# plot_region(lon, lat, diff, extent=[-180,0, 10, 80])