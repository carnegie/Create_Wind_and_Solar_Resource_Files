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


# In[2]:


# import shapefile
# Shapefiles for Africa can be found here: http://www.maplibrary.org/library/stacks/Africa/index.htm
# below uses a default shape file saved in this repository to ensure the code runs.
fname = 'data/US_Interconnects/WesternInterconnect.shp' #change directory
if fname == 'data/US_Interconnects/WesternInterconnect.shp':
    print(f"\n\n\033[0;33mYou should probably change this example path, {fname}, to something you downloaded for your new region\033[0m\n\n")
SA_shp= gpd.read_file(fname)
SA = SA_shp.geometry


# In[3]:


# Read the variable "SWGDN" from "SWGDN.nc" and get lat/lon info;
f_axis = cdms.open('data/SWGDN.nc')
v=f_axis('SWGDN')
lat=v.getAxis(1)  # latitude
lon=v.getAxis(2)  # longitude
f_axis.close()


# In[4]:


#create mask
SA_poly=regionmask.Regions(SA)
mask = np.ma.masked_invalid(SA_poly.mask(lon, lat))


# In[22]:


#formatting
mask_SA_out = MV.array(mask)
mask_SA_out.id='mask_SoutAfrica'
mask_SA_out.setAxis(0,lat)
mask_SA_out.setAxis(1,lon)


# In[23]:


#safe it as a .nc file
print("\n\033[0;33mSaving file as selected_masks_SouthAfrica.nc\033[0m\n")
g=cdms.open('selected_masks_SouthAfrica.nc','w')
g.write(mask_SA_out)
g.close()

