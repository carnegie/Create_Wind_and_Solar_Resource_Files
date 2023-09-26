#!/usr/bin/env python
# coding: utf-8

# In[1]:


import cdms2 as cdms, MV2 as MV
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import shapefile as shp 
import numpy as np
import regionmask


# Keeping region_name == WesternInterconnect will allow you to run a working example
# for step1p2 as well.
region_name = 'WesternInterconnect'

# In[2]:


# import shapefile
# Shapefiles for Africa can be found here: http://www.maplibrary.org/library/stacks/Africa/index.htm
# below uses a default shape file saved in this repository to ensure the code runs.
fname = f'data/US_Interconnects/{region_name}.shp' #change directory
if fname == 'data/US_Interconnects/WesternInterconnect.shp':
    print(f"\n\n\033[0;33mYou should probably change this example path, {fname}, to something you downloaded for your new region\033[0m\n\n")
shp = gpd.read_file(fname)
region = shp.geometry


# In[3]:


# Read the variable "SWGDN" from "SWGDN.nc" and get lat/lon info;
f_axis = cdms.open('data/SWGDN.nc')
v=f_axis('SWGDN')
lat=v.getAxis(1)  # latitude
lon=v.getAxis(2)  # longitude
f_axis.close()


# In[4]:


#create mask
poly=regionmask.Regions(region)
mask = np.ma.masked_invalid(poly.mask(lon, lat))


# In[22]:


#formatting
mask_out = MV.array(mask)
mask_out.id=f'mask_{region_name}'
mask_out.setAxis(0,lat)
mask_out.setAxis(1,lon)


# In[23]:


#save it as a .nc file
print(f"\n\033[0;33mSaving file as selected_masks_{region_name}.nc\033[0m\n")
g=cdms.open(f'selected_masks_{region_name}.nc','w')
g.write(mask_out)
g.close()

