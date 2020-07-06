# From Lei Duan

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
from matplotlib import pyplot as plt


#from matplotlib.colors import ListedColormap, LinearSegmentedColormap
ax = plt.subplot(111, projection = ccrs.PlateCarree())
ax.set_global()
ax.add_feature(cfeature.COASTLINE)

# Plot western interconnect
fname = 'data/US_Interconnects/WesternInterconnect.shp'
shape_feature = ShapelyFeature(Reader(fname).geometries(),
                                ccrs.PlateCarree(), edgecolor='black')
ax.add_feature(shape_feature, facecolor='blue')

#ax.pcolormesh( lon, lat, test1, transform=ccrs.PlateCarree() )
#ax.set_extent([-150,-50, 10, 80])
plt.show()
