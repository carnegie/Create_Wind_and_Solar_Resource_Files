import cdms2 as cdms, MV2 as MV, cdutil, numpy as np

### Step 0, prepare
# Again, get lat/lon information
f_axis = cdms.open('data/SWGDN.nc')
v=f_axis('SWGDN')
lat=v.getAxis(1) 
lon=v.getAxis(2)
f_axis.close()  
# Get land mask
f_land_mask = cdms.open('data/land_sea_mask_merra.nc4')
land_mask_tmp = f_land_mask('FRLAND',squeeze=1)
land_mask_tmp[land_mask_tmp>=0.5] = 1.
land_mask_tmp[land_mask_tmp<0.5]  = 0.
land_mask = MV.array(MV.masked_equal(land_mask_tmp,0.))
land_mask.setAxis(0,lat);      land_mask.setAxis(1,lon)
f_land_mask.close()
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
        masked_sCF = sCF
        masked_wCF = wCF
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
        s_avg_tmp = cdutil.averager(masked_sCF,axis='yx')
        w_avg_tmp = cdutil.averager(masked_wCF,axis='yx')
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
        s_avg_tmp = cdutil.averager(masked_sCF,axis='yx')
        w_avg_tmp = cdutil.averager(masked_wCF,axis='yx')
    print ("Averaged solar capacity factor for the filtered grids is: ", s_avg_tmp)
    print ("Averaged wind capacity factor for the filtered grids is: ", w_avg_tmp)
    return masked_sCF, masked_wCF


### Step 1
# The selection of grids are based on annual mean or decadal mean global CFs data;
# For the code below, I first downloaded the annual mean solar and wind CFs data
# between 2009 and 2018 and calculated the decadal mean global CFs data; 
# The variables "scf" and "wcf" are decadal mean results, and are further used below;
data_path = 'Where you put the downloaded annual mean data (ends with "annual" on MEMEX)'
scf = np.zeros([len(lat), len(lon)])
wcf = np.zeros([len(lat), len(lon)])
for i in range(10):
    sf = cdms.open(data_path + str(i+2009) +'_scf_annual.nc')
    wf = cdms.open(data_path + str(i+2009) +'_wcf100m031225_annual.nc')
    scf = scf + sf('scf_annual')/10.
    wcf = wcf + wf('wcf_annual')/10.
    sf.close()
    wf.close()

### Step 2
# Take the NYS as an example:
# I first read the NYS mask created in the previous step
fmask=cdms.open('selected_masks_NYSTEX.nc')
mask_NYS= fmask('mask_NYS')
fmask.close()
# Now I used the NYS mask and land mask to filter the decadal mean solar and wind CFs;
# Note that both scf and wcf are 2D array because we did the time average: (lat, lon)
# The returned array (scf_NYS, wcf_NYS) conains decadal mean values of solar/wind CFs for NYS and over land only; 
scf_NYS = scf * mask_NYS * land_mask
wcf_NYS = wcf * mask_NYS * land_mask
# Now we can further selected grids:
# If I want all grids of NYS:
s_mask_NYS, w_mask_NYS = select_CF(scf_NYS, wcf_NYS, 1)
# If I want grids above the thresholds (note that you can change the threshold youself):
s_mask_NYS, w_mask_NYS = select_CF(scf_NYS, wcf_NYS, 2)
# If I want grids that have the top X% largest values (note that you can change the threshold youself):
s_mask_NYS, w_mask_NYS = select_CF(scf_NYS, wcf_NYS, 3)
# Set the name for these two mask variables
s_mask_NYS.id = 'smask_NYS'
w_mask_NYS.id = 'wmask_NYS'
# Now write these two mask variables to a NetCDF file for further use
g=cdms.open('selected_mask_NYSTEX_25%.nc','w')
g.write(s_mask_NYS)
g.write(w_mask_NYS)
g.close()
