########
# Most of the wind script is the same with that in solar
# The reason to separate these two is because when you deal with solar and wind 
# at the same time, you could take too much memeory
########


import cdms2 as cdms, MV2 as MV, cdutil, numpy as np, sys,calendar

def get_prefix_name(year):
    if year <= 1991:
        prefix_name = "MERRA2_100.tavg1_2d_slv_Nx."
    if year > 1991 and year <= 2000:
        prefix_name = "MERRA2_200.tavg1_2d_slv_Nx."
    if year > 2000 and year <= 2010:
        prefix_name = "MERRA2_300.tavg1_2d_slv_Nx."
    if year > 2010:
        prefix_name = "MERRA2_400.tavg1_2d_slv_Nx."
    return prefix_name

if len(sys.argv) == 1:
    year = 2016
else:
    year = sys.argv[1]

data_patch = '/lustre/scratch/leiduan/MERRA2_data/'
case_name = get_prefix_name(int(year))+str(year)+'_wcf100m031225.nc'
isleap = calendar.isleap(int(year))
if isleap == True:
    leap_year = 1
else:
    leap_year = 0

f_mask = cdms.open('SWGDN.nc')
v=f_mask('SWGDN')
lat=v.getAxis(1)
lon=v.getAxis(2)
f_mask.close()

fw = cdms.open(data_patch+case_name)
wcf = MV.array(fw('wcf',squeeze=1))
wcf[wcf<0] = 0.
wcf[wcf>1] = 1.
fw.close()


# use NetCDF3 Classic format
cdms.setNetcdfShuffleFlag(0)      # netcdf3 classic...
cdms.setNetcdfDeflateFlag(0)      # netcdf3 classic...
cdms.setNetcdfDeflateLevelFlag(0) # netcdf3 classic...

fm = cdms.open('selected_mask_NYS.nc')
region_mask_list = {0:'wmask_NYS'}
mask_idx = MV.array(fm(region_mask_list[idx]))
# Pre-define the output variable and output file
g=cdms.open('averaged_NYS_wcf'+str(year)+'.nc','w')
new_data = MV.array(np.zeros(len_axis))
new_data.id = 'averaged_' + region_mask_list[0]
for i in range(len_axis):
    scf_idx = scf[i] * mask_idx
    scf_idx.setAxis(0,lat)
    scf_idx.setAxis(1,lon)
    # If lat/lon info is given, the following average function calculate the 
    # area weighted mean
    new_data[i] = cdutil.averager(scf_idx, axis='yx')
g.write(new_data)
g.close()