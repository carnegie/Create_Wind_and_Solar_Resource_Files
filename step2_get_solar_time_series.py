import cdms2 as cdms, MV2 as MV, cdutil, numpy as np, sys,calendar
import os
from helpers import get_prefix_name


print("\nRunning ")
print(sys.argv[0])
print("Input arg list")
print(sys.argv)


# Default year is 2016 when no year info is provided
if len(sys.argv) == 1:
    year = 2016
else:
    year = int(sys.argv[1])

if len(sys.argv) > 1:
    region = sys.argv[2]
else:
    region = 'NYS'

if len(sys.argv) > 2:
    mthd = int(sys.argv[3])
else:
    mthd = 1

if len(sys.argv) > 3:
    date = sys.argv[4]
else:
    date = 'June23'

if len(sys.argv) > 4:
    scf_or_wcf = sys.argv[5]
else:
    scf_or_wcf = 'scf'

print("Processing for year %i, region %s, with selection method %i, for %s" % (year, region, mthd, scf_or_wcf))

# Data path to find the solar/wind CFs;
# Name of data to open based on year;
# The total hour length is different for leap and non-leap year;
data_patch = '/lustre/scratch/leiduan/MERRA2_data/MERRA2_CF_Data/'
app = 'scf' if scf_or_wcf == 'scf' else 'wcf100m031225'
is_solar = True if scf_or_wcf == 'scf' else False
case_name = get_prefix_name(int(year), is_solar)+str(year)+'_'+app+'.nc'
isleap = calendar.isleap(int(year))
if isleap == True:
    leap_year = 1
else:
    leap_year = 0

# Gat lat/lon info
f_mask = cdms.open('data/SWGDN.nc')
v=f_mask('SWGDN')
lat=v.getAxis(1)
lon=v.getAxis(2)
f_mask.close()

# Get hourly solar data
fs = cdms.open(data_patch+case_name)
cfs = MV.array(fs(scf_or_wcf, squeeze=1))
cfs[cfs<0] = 0.
cfs[cfs>1] = 1.
fs.close()
len_axis = len(cfs.getAxis(0))

# These are to set the output format, you can ignore these lines
# Use NetCDF3 Classic format
cdms.setNetcdfShuffleFlag(0)      # netcdf3 classic...
cdms.setNetcdfDeflateFlag(0)      # netcdf3 classic...
cdms.setNetcdfDeflateLevelFlag(0) # netcdf3 classic...

# Read the masks you created in previous step, provided the name below
fm = cdms.open('selected_mask_outfile.nc')
region_mask_list = 'smask_%s_mthd%i' % (region, mthd)
mask_idx = MV.array(fm(region_mask_list))
# Make path for saving files
if not os.path.exists('outfiles'):
    os.makedirs('outfiles')
if not os.path.exists('outfiles/%s_%s_mthd%i' % (date, region, mthd)):
    os.makedirs('outfiles/%s_%s_mthd%i' % (date, region, mthd))
# Pre-define the output variable and output file
g=cdms.open('outfiles/%s_%s_mthd%i/averaged_%s_%s%i.nc' % (date, region, mthd, region, scf_or_wcf, year),'w')
new_data = MV.array(np.zeros(len_axis))
new_data.id = 'averaged_' + region_mask_list
for i in range(len_axis):
    print(i)
    cfs_idx = cfs[i] * mask_idx
    cfs_idx.setAxis(0,lat)
    cfs_idx.setAxis(1,lon)
    # If lat/lon info is given, the following average function calculate the 
    # area weighted mean
    new_data[i] = cdutil.averager(cfs_idx, axis='yx')
g.write(new_data)
g.close()
