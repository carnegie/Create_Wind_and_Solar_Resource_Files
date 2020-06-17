import cdms2 as cdms, numpy as np, MV2 as MV, geopandas as gpd, regionmask
from shapely.geometry import MultiPolygon



### Step 0 
# Read the variable "SWGDN" from "SWGDN.nc" and get lat/lon info;
f_axis = cdms.open('data/SWGDN.nc')
v=f_axis('SWGDN')
lat=v.getAxis(1)  # latitude
lon=v.getAxis(2)  # longitude
f_axis.close()



### Step 1
# Seprate land and ocean grids; 
f_land_mask = cdms.open('data/land_sea_mask_merra.nc4')
land_mask_tmp = f_land_mask('FRLAND',squeeze=1) # land fraction
# We set grids with "FRLAND" >= 0.5 as land, and have a value of 1;
# Other grids ("FRLAND" < 0.5) are treated as ocean, and have a value of 0;
land_mask_tmp[land_mask_tmp>=0.5] = 1.
land_mask_tmp[land_mask_tmp<0.5]  = 0.
# Masked all ocean grids, and the returned ocean grids have no value at all ("-"); 
# To faciliate average process later, we set the lat/lon to the returned array;
land_mask = MV.array(MV.masked_equal(land_mask_tmp,0.))
land_mask.setAxis(0,lat);      land_mask.setAxis(1,lon)
f_land_mask.close()



### Step 2
# Depends on the shapefiles downloaded, this section could be slightly different;
# From regionmask and Nature Earth, create NYS and Texas masks;
states = regionmask.defined_regions.natural_earth.us_states_50
mask = np.array(states.mask(lon, lat, wrap_lon=False))
NY = np.ma.masked_not_equal(mask, 34)*0.+1.
TX = np.ma.masked_not_equal(mask, 43)*0.+1.

""" 
# Here is another example using shapefiles and geopandas;
# This could be done using regionmask as well;

def generate_mask_from_geometry(lat1d, lon1d, lat2d, lon2d, geometry):
    mask = []
    for lat3, lon3 in zip(lat1d, lon1d):
        this_point = gpd.geoseries.Point(lon3,lat3)
        res = geometry.contains(this_point)
        if res.values[0]:
            mask.append(1)
        else:
            mask.append(0)
    mask_2d = np.array(np.array(mask).reshape(lon2d.shape))
    return mask_2d

WI_shp= gpd.read_file('./Interconnects2/WesternInterconnect.shp') # These are some shapefiles I downloaded bfore
WI = WI_shp.geometry
EI_shp= gpd.read_file('./Interconnects2/EasternInterconnect.shp')
EI = EI_shp.geometry
TI_shp= gpd.read_file('./Interconnects2/TexasInterconnect.shp')
TI = TI_shp.geometry

lon1, lat1 = np.meshgrid(lon,lat)
lon2 = lon1.reshape(-1)
lat2 = lat1.reshape(-1)

mask_WI = generate_mask_from_geometry(lat2, lon2, lat1, lon1, WI)
mask_WI_out = MV.array(mask_WI); mask_WI_out.id='mask_WI'; mask_WI_out.setAxis(0,lat); mask_WI_out.setAxis(1,lon)

mask_EI = generate_mask_from_geometry(lat2, lon2, lat1, lon1, EI)
mask_EI_out = MV.array(mask_EI); mask_EI_out.id='mask_EI'; mask_EI_out.setAxis(0,lat); mask_EI_out.setAxis(1,lon)

mask_TI = generate_mask_from_geometry(lat2, lon2, lat1, lon1, TI)
mask_TI_out = MV.array(mask_TI); mask_TI_out.id='mask_TI'; mask_TI_out.setAxis(0,lat); mask_TI_out.setAxis(1,lon)

# End of example
"""


# For the derived NYS and Texas masks, give them name, lat, and lon info;
mask_NYS_out = MV.array(NY)
mask_NYS_out.id='mask_NYS'
mask_NYS_out.setAxis(0,lat)
mask_NYS_out.setAxis(1,lon)

mask_TEX_out = MV.array(TX)
mask_TEX_out.id='mask_TEX'
mask_TEX_out.setAxis(0,lat)
mask_TEX_out.setAxis(1,lon)

# Create a new NetCDF file and write these two variables into it for later use;
g=cdms.open('selected_masks_NYS.nc','w')
g.write(mask_NYS_out)
g.write(mask_TEX_out)
g.close()
