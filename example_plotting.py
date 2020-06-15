# From Lei Duan

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib import pyplot as plt
#from matplotlib.colors import ListedColormap, LinearSegmentedColormap
ax1 = plt.subplot(111, projection = ccrs.PlateCarree())
ax1.set_global()
ax1.add_feature(cfeature.COASTLINE)
ax1.pcolormesh( lon, lat, test1, transform=ccrs.PlateCarree() )
#ax1.set_extent([-150,-50, 10, 80])
plt.show()
plt.clf()
