import numpy as np
import sys
import geopandas as gpd, regionmask
import cdms2 as cdms
import MV2 as MV

# Currently set up for whole 'US' or ISOs
# regions = ['US']
regions = ['CISO', 'MISO', 'ERCOT', 'ISNE']

# 'ERA5' or 'MERRA2'
weather_data = 'MERRA2'

# When using ERA5:
if weather_data == 'ERA5':
    fmask = cdms.open('data/ERA5_landsea_mask.nc')
    land_mask_tmp = fmask('lsm', squeeze=1)[0]
# When using MERRA2:
elif weather_data == 'MERRA2':
    fmask = cdms.open('../example_MERRA2/data/land_sea_mask_merra.nc4')
    land_mask_tmp = fmask('FRLAND',squeeze=1)
else:
    print(f"Data source {weather_data} not recognized, aborting.")
    sys.exit()

lat = land_mask_tmp.getAxis(0)
lon = land_mask_tmp.getAxis(1)
fmask.close()

land_mask_tmp[land_mask_tmp>=0.5] = 1.
land_mask_tmp[land_mask_tmp<0.5]  = 0.
land_mask = MV.array(MV.masked_equal(land_mask_tmp,0.))
land_mask.setAxis(0,lat);      land_mask.setAxis(1,lon)

# Order of ISOs in the shapefile
ISO_dict = {0: 'MISO', 1: 'SPP', 2: 'PJM', 3: 'ERCOT', 4: 'CISO', 5: 'ISNE', 6: 'NYISO'}

# ------------------------------------------------------------------------
# """

for region in regions:

    if region == 'US':
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
        out_path = ''

    elif region in ISO_dict.values():
        ISOs = gpd.read_file('data/Independent_System_Operators.shx')
        # Get dictionary key from value
        ISO_index = list(ISO_dict.values()).index(region)
        selected_ISO = ISOs.iloc[[ISO_index]]
        mask = regionmask.mask_geopandas(selected_ISO, lon, lat)
        mask_masked = np.ma.masked_invalid(mask)
        out_path = 'create_ISO_files/'

    else:
        print(f"Region {region} not recognized, aborting.")
        continue

    mask = MV.array(mask_masked)
    mask.setAxis(0,lat)
    mask.setAxis(1,lon)
    mask.id = f'mask_{region}'

    ### Create a new NetCDF file and save the mask
    g=cdms.open(out_path + f'step1p1_selected_masks_{region}.nc','w')
    g.write(mask)
    g.close() 



