import cdms2 as cdms, MV2 as MV, cdutil, numpy as np

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



# This function is used to set lat/lon info for a given array
def set_axes(var):
    var_new = MV.array(var)
    var_new.setAxis(0,lat)
    var_new.setAxis(1,lon)
    return var_new
# This function is used to further filter grids based on different purposes
# idx == 1: use all grids for the interested region;
# idx == 2: set thresholds for wind and solar, separately, and filter values lower than that;
# idx == 3: take the top X% amount of grids (note not area) for the interested region;
# Return the derived solar and wind masks
# Note that this is based on annual mean (or decadal mean) capacity factor;
def select_CF(sCF, wCF, idx, *i):
    if idx == 1.:
        masked_sCF = np.ceil(sCF)
        masked_wCF = np.ceil(wCF)
        s_avg_tmp = cdutil.averager(sCF,axis='yx')
        w_avg_tmp = cdutil.averager(wCF,axis='yx')
    elif idx == 2.:
        # set threshold;
        # you can change this values based on needs;
        s_thresholds = 0.26
        w_thresholds = 0.26
        # set grids with values lower than the threshold to 0;
        sCF[sCF<s_thresholds] = 0.
        wCF[wCF<w_thresholds] = 0.
        # mask grids with a value of 0 (grids that are not needed);
        masked_sCF = set_axes(MV.masked_equal(sCF,0.)*0.+1)
        masked_wCF = set_axes(MV.masked_equal(wCF,0.)*0.+1)
        s_avg_tmp = cdutil.averager(masked_sCF*sCF,axis='yx')
        w_avg_tmp = cdutil.averager(masked_wCF*wCF,axis='yx')
    elif idx ==3.:
        # set threshold, top X%;
        # you can change this values based on needs;
        p_threshold_s = 0.25
        p_threshold_w = 0.25
        # sort all grids, values for grids that are
        # outside the interested region are set to -1;
        s_reshape = np.sort(np.array(MV.filled(sCF,-1)).ravel())[::-1]
        w_reshape = np.sort(np.array(MV.filled(wCF,-1)).ravel())[::-1]
        # remove grids with values of -1;
        s_no_minus1 = s_reshape[s_reshape!=-1]
        w_no_minus1 = w_reshape[w_reshape!=-1]
        # find the threshold for the top X%   
        num_s = int(len(s_no_minus1)*p_threshold_s)
        num_w = int(len(w_no_minus1)*p_threshold_w)
        s_thresholds = s_no_minus1[num_s-1]
        w_thresholds = w_no_minus1[num_w-1]
        # mask grids with a value lower than the derived thresholds (grids that are not needed);
        masked_sCF = set_axes( MV.masked_less(sCF,s_thresholds)*0.+1 )
        masked_wCF = set_axes( MV.masked_less(wCF,w_thresholds)*0.+1 )
        s_avg_tmp = cdutil.averager(masked_sCF*sCF,axis='yx')
        w_avg_tmp = cdutil.averager(masked_wCF*wCF,axis='yx')
    print(f"For method {idx}, averaged solar capacity factor for the filtered grids is: {s_avg_tmp}")
    print(f"For method {idx}, averaged wind capacity factor for the filtered grids is: {w_avg_tmp}")
    print(f"Selected grid cells solar {np.ceil(masked_sCF).sum()}\nSelected grid cells wind {np.ceil(masked_wCF).sum()}")
    return masked_sCF, masked_wCF


### Step 1
# The selection of grids are based on annual mean or decadal mean global CFs data;
# For the code below, I first downloaded the annual mean solar and wind CFs data
# between 2009 and 2018 and calculated the decadal mean global CFs data; 
# The variables "scf" and "wcf" are decadal mean results, and are further used below;
data_path = './example/example_data/'
start_year = 2011
n_years = 10
scf = np.zeros([len(lat), len(lon)])
wcf = np.zeros([len(lat), len(lon)])
for i in range(n_years):
    year = i + start_year
    file_name = 'Annual_ERA5_2011_12_Org.nc'
    file_open = cdms.open(f"{data_path}{file_name}")
    scf = scf + file_open('annual_scf')/float(n_years)
    wcf = wcf + file_open('annual_wcf')/float(n_years)
    file_open.close()

def make_grid_cell_selections(scf, wcf, region_mask, land_mask, selection_method, region_name, out_file):

    scf_region = set_axes(scf * region_mask * land_mask)
    wcf_region = set_axes(wcf * region_mask * land_mask)
    # Now we can further selected grids:
    s_mask_region, w_mask_region = select_CF(scf_region, wcf_region, selection_method)
    # Set the name for these two mask variables
    s_mask_region.id = f'smask_{region_name}_mthd{selection_method}'
    w_mask_region.id = f'wmask_{region_name}_mthd{selection_method}'
    # Now write these two mask variables to a NetCDF file for further use
    out_file.write(s_mask_region)
    out_file.write(w_mask_region)

    # Return the selected masks, and the decadal mean CFs for the selected region
    return s_mask_region, w_mask_region, scf_region * s_mask_region, wcf_region * w_mask_region


### Step 2
# Take the NYS as an example:
# I first read the NYS mask created in the previous step
fmask=cdms.open(f'./example/selected_masks_US.nc')
g=cdms.open(f'./example/selected_USmask_outfile_ERA5.nc','w') # out_file
results = {}
for region_name in ['US'] : 
    print(f"REGION: {region_name}")
    mask_region= fmask(f'mask_{region_name}')
    # Now I used the NYS mask and land mask to filter the decadal mean solar and wind CFs;
    # Note that both scf and wcf are 2D array because we did the time average: (lat, lon)
    # The returned array (scf_region, wcf_region) conains decadal mean values of solar/wind CFs for NYS and over land only; 

    results[region_name] = {}
    # If I want all grids of NYS: selection_method = 1
    # If I want grids above the thresholds (note that you can change the threshold youself): selection_method = 2
    # If I want grids that have the top X% largest values (note that you can change the threshold youself): selection_method = 3
    for i in [ 1, 2, 3]:
    #selection_method = 1
        results[region_name][i] = make_grid_cell_selections(scf, wcf, mask_region, land_mask, i, region_name, g)


print("\nSaving masks to:")
print(g)
g.close()




stop 

#---------------------------------------------
# Below for plotting results if you care
# Motivated by Muriel Hauser's code
#---------------------------------------------


plot_masks = True
if not plot_masks:
    exit()

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib import pyplot as plt
import os

if not os.path.exists('plots'):
    os.makedirs('plots')

def plot_region(lon, lat, mask_region, save_name, extent=[-150,-50, 10, 80]):
    plt.close()
    print(save_name)
    ax = plt.subplot(111, projection = ccrs.PlateCarree())
    ax.set_global()
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.STATES)
    
    im = ax.pcolormesh( lon, lat, mask_region, transform=ccrs.PlateCarree() )
    cbar = ax.figure.colorbar(im)
    name = "resource annual capacity factors" if '_weighted' in save_name else "selected region"
    cbar.ax.set_ylabel(name)
    
    ax.set_extent(extent)
    
    plt.savefig(f'plots/{save_name}.png')

extents = {
        'default' : [-150,-50, 10, 80], # Good CONUS window
        'NYS' : [-85,-60, 35, 50],
        'NYIS_2018' : [-85,-60, 35, 50],
        'PJM_2018' : [-95,-65, 30, 45],
        'TEX' : [-110, -85, 20, 40],
        'TI' : [-110, -85, 20, 40],
        'ERCO_2018' : [-110, -85, 20, 40],
        }


# matplotlib pcolormesh plots points based on the lower left coordinate
# to center the value when plotted, provide shifted coordinates.
dlat = 0.5 # From inspection of lat and lon
dlon = 0.625 
plot_shifted_lon = [i - dlon/2. for i in lon]
plot_shifted_lat = [i - dlat/2. for i in lat]

for region_name in ['NYS', 'TEX',]:# 'NYIS_2018', 'TI', 'ERCO_2018', 'PJM_2018']:

    print(region_name)

    mask_region = fmask(f'mask_{region_name}')
    plot_region(plot_shifted_lon, plot_shifted_lat, mask_region, f'{region_name}_full_region', extents[region_name])

    for mthd in [1, 2, 3]:
        # Plot the selected region
        plot_region(plot_shifted_lon, plot_shifted_lat, results[region_name][mthd][0], f'{region_name}_{mthd}_solar_selected', extents[region_name])
        plot_region(plot_shifted_lon, plot_shifted_lat, results[region_name][mthd][1], f'{region_name}_{mthd}_wind_selected', extents[region_name])

        # Plot the decadal mean resources for the selected region
        plot_region(plot_shifted_lon, plot_shifted_lat, results[region_name][mthd][2], f'{region_name}_{mthd}_solar_weighted', extents[region_name])
        plot_region(plot_shifted_lon, plot_shifted_lat, results[region_name][mthd][3], f'{region_name}_{mthd}_wind_weighted', extents[region_name])



fmask.close()
