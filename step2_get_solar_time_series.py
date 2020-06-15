import cdms2 as cdms, MV2 as MV, cdutil, numpy as np, sys,calendar

# This function is used to find CFs data name
def get_prefix_name(year):
    if year <= 1991:
        prefix_name = "MERRA2_100.tavg1_2d_rad_Nx."
    if year > 1991 and year <= 2000:
        prefix_name = "MERRA2_200.tavg1_2d_rad_Nx."
    if year > 2000 and year <= 2010:
        prefix_name = "MERRA2_300.tavg1_2d_rad_Nx."
    if year > 2010:
        prefix_name = "MERRA2_400.tavg1_2d_rad_Nx."
    return prefix_name

# Default year is 2016 when no year info is provided
if len(sys.argv) == 1:
    year = 2016
else:
    year = sys.argv[1]

# Data path to find the solar/wind CFs;
# Name of data to open based on year;
# The total hour length is different for leap and non-leap year;
data_patch = '/lustre/scratch/leiduan/MERRA2_data/'
case_name = get_prefix_name(int(year))+str(year)+'_scf.nc'
isleap = calendar.isleap(int(year))
if isleap == True:
    leap_year = 1
else:
    leap_year = 0

# Gat lat/lon info
f_mask = cdms.open('SWGDN.nc')
v=f_mask('SWGDN')
lat=v.getAxis(1)
lon=v.getAxis(2)
f_mask.close()

# Get hourly solar data
fs = cdms.open(data_patch+case_name)
scf = MV.array(fs('scf',squeeze=1))
scf[scf<0] = 0.
scf[scf>1] = 1.
fs.close()
len_axis = len(scf.getAxis(0))

# These are to set the output format, you can ignore these lines
# Use NetCDF3 Classic format
cdms.setNetcdfShuffleFlag(0)      # netcdf3 classic...
cdms.setNetcdfDeflateFlag(0)      # netcdf3 classic...
cdms.setNetcdfDeflateLevelFlag(0) # netcdf3 classic...

# Read the masks you created in previous step, provided the name below
fm = cdms.open('selected_mask_NYS.nc')
region_mask_list = {0:'smask_NYS'}
mask_idx = MV.array(fm(region_mask_list[idx]))
# Pre-define the output variable and output file
g=cdms.open('averaged_NYS_scf'+str(year)+'.nc','w')
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