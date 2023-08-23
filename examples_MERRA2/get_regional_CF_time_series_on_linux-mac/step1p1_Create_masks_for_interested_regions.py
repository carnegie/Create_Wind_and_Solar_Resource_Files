import cdms2 as cdms, numpy as np, MV2 as MV, geopandas as gpd, regionmask
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
import pandas as pd



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
# Tyler was not having success with this section of the code. See alternative
# example below for making masks from shapefiles and other geometries


# Here is another example using shapefiles and geopandas;
# This could be done using regionmask as well;

def generate_mask_from_geometry(lat1d, lon1d, lat2d, lon2d, geometry):
    mask = []
    for lat3, lon3 in zip(lat1d, lon1d):
        this_point = Point(lon3,lat3)
        res = geometry.contains(this_point)
        if res.values[0]:
            mask.append(1)
        else:
            mask.append(0)
    mask_2d = np.array(np.array(mask).reshape(lon2d.shape))
    return mask_2d

WI_shp= gpd.read_file('data/US_Interconnects/WesternInterconnect.shp') # These are some shapefiles I downloaded bfore
WI = WI_shp.geometry
EI_shp= gpd.read_file('data/US_Interconnects/EasternInterconnect.shp')
EI = EI_shp.geometry
TI_shp= gpd.read_file('data/US_Interconnects/TexasInterconnect.shp')
TI = TI_shp.geometry

lon1, lat1 = np.meshgrid(lon,lat)
lon2 = lon1.reshape(-1)
lat2 = lat1.reshape(-1)

print("Mask for: mask_WI (this takes 15 seconds)")
mask_WI = generate_mask_from_geometry(lat2, lon2, lat1, lon1, WI)
mask_WI_out = MV.array(mask_WI); mask_WI_out.id='mask_WI'; mask_WI_out.setAxis(0,lat); mask_WI_out.setAxis(1,lon)

print("Mask for: mask_EI (this takes 15 seconds)")
mask_EI = generate_mask_from_geometry(lat2, lon2, lat1, lon1, EI)
mask_EI_out = MV.array(mask_EI); mask_EI_out.id='mask_EI'; mask_EI_out.setAxis(0,lat); mask_EI_out.setAxis(1,lon)

print("Mask for: mask_TI (this takes 15 seconds)")
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
g=cdms.open('selected_masks.nc','w')
g.write(mask_NYS_out)
g.write(mask_TEX_out)


"""
# Alternative example for creating masks.
# Use the regionmask.Regions class which is what is retrieved from Lei's working
# code example using regionmask.defined_regions.natural_earth.us_states_50.


def make_and_save_mask(geom, lon, lat, mask_name, save_file):

    # Some are Polygons others are MultiPolygons
    # and regionmask.Regions requires a list.
    try:
        regions = regionmask.Regions(geom)
    except TypeError:
        regions = regionmask.Regions([geom,])
    regions_mask = np.array(regions.mask(lon, lat, wrap_lon=False))
    masked_array = np.ma.masked_not_equal(regions_mask, 0)*0.+1.
    mask_out = MV.array(masked_array)
    mask_out.id=mask_name
    mask_out.setAxis(0,lat)
    mask_out.setAxis(1,lon)
    
    save_file.write(mask_out)
    print(f"Saved mask {mask_name} with {mask_out.sum()} selected cells")

    return save_file



TI_shp= gpd.read_file('data/US_Interconnects/TexasInterconnect.shp')
g = make_and_save_mask(
        TI_shp.geometry, lon, lat, 'mask_TI', g
        )

# You must download this file from gDrive, it was created by Zane from the
# Catalyst Collective and is not technically a finished producte yet (22 June 2020).
# It contains the yearly reported balancing authority boundaries as reported to EIA.
# Warning, file is 500 MB
# Download from gDrive: Wind_and_Solar_CF_Files/planning_areas_ferc714.gpkg.gz
# https://drive.google.com/drive/u/0/folders/1158yObOGB4O41nz74GISGQgmCGSXe1rk
ba_info_file = "./planning_areas_ferc714.gpkg"
ba_df = gpd.read_file(ba_info_file)

# Skim a subset for coordinate conversion
ba_df = ba_df[
    (ba_df['balancing_authority_code_eia'] == 'ERCO') |
    (ba_df['balancing_authority_code_eia'] == 'NYIS') |
    (ba_df['balancing_authority_code_eia'] == 'PJM')
    ]

# Find the index for the most recent EIA map (these change quite a bit and are worth exploring
# if you are doing a detailed analysis of this!)
tgt_year = 2018 # most recent year in file.

# Make dates datetime
ba_df['report_date'] = pd.to_datetime(ba_df['report_date'])

to_keep = []
for idx in ba_df.index:
    if ba_df.loc[idx, 'report_date'].year == tgt_year :
        to_keep.append(idx)

ba_df = ba_df.loc[to_keep]

# Convert coordinates
# WGS84 latitude-longitude CRS (same as the interconnects in shapefiles)
ba_df = ba_df.to_crs("EPSG:4326") 

# For quicker iterating if there's an error, save a tmp slimmed version of the .gpkg file
ba_df.to_file("new.gpkg", driver="GPKG")
ba_df = gpd.read_file("new.gpkg")

# Make dates datetime
ba_df['report_date'] = pd.to_datetime(ba_df['report_date'])


bas = {
        'ERCO' : 'ERCOT',
        'NYIS' : 'New York Independent System Operator, Inc.',
        'PJM' : 'PJM Interconnection LLC' # Note PJM also reports FERC results
        # by multiple hubs. The selected one here is the aggregate.
    }

for k, v in bas.items() :
    print(k, v)

    g = make_and_save_mask(
            ba_df[ba_df['respondent_name_ferc714'] == v].geometry,
            lon, lat, f'mask_{k}_{tgt_year}', g
            )


"""




g.close()
