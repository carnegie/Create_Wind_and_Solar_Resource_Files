import cdms2 as cdms
import MV2 as MV
import numpy as np
import sys, cdutil, os

print("\nRunning ")
print(sys.argv[0])
print("Input arg list")
print(sys.argv)

# Default year is 2019 when no year info is provided
year = 2019 if len(sys.argv) <= 1 else int(sys.argv[1])
region = 'US' if len(sys.argv) <= 2 else sys.argv[2]
mthd = 1 if len(sys.argv) <= 3 else int(sys.argv[3])
date = 'Nan' if len(sys.argv) <= 4 else sys.argv[4]
scf_or_wcf = 'scf' if len(sys.argv) <= 5 else sys.argv[5]
source = 'Nan' if len(sys.argv) <= 6 else sys.argv[6]
mask = 'Nan' if len(sys.argv) <= 7 else sys.argv[7]

if source != mask:
    print(f"Source and mask are not consistent, make sure this is correct!.")


if source == 'ERA5':
    # landsea file
    weather_data_path = 'data/ERA5_landsea_mask.nc'
    # CF files created with step 0
    cfs_data_path = '/carnegie/nobackup/scratch/Climate_Energy_Lab/CFs/ERA5_Org/'

elif source == 'MERRA2': 
    # landsea file
    weather_data_path = '../example_MERRA2/data/land_sea_mask_merra.nc4'
    # CF files created with step 0
    cfs_data_path = '/carnegie/nobackup/scratch/Climate_Energy_Lab/CFs/MERRA2/'

else:
    print(f"Data source {source} not recognized, aborting.")
    sys.exit()


pre = 's' if scf_or_wcf == 'scf' else 'w'
f_mask = cdms.open(weather_data_path)
app = 'SolarCFs_' if scf_or_wcf == 'scf' else 'WindCFs_'
case_name = []
if source == 'ERA5':
    app += 'ERA5_'
    v = f_mask('lsm', squeeze=1)[0]
    suff = '_Org' 
    for month_idx in np.arange(1, 13, 1):
        case_name.append(app + str(year) + '_' + str(month_idx) + suff + '.nc')
else:
    v = f_mask('FRLAND',squeeze=1)
    case_name.append(app + str(year) + '.nc')
lat = v.getAxis(0)
lon = v.getAxis(1)
f_mask.close() 

fm = cdms.open(f'step1p2_selected_{region}mask_outfile_{source}.nc')


# Region to do list and corresponding mask file:
LetterCode = [region]

for reg_idx in LetterCode:
    region = reg_idx
    region_mask = pre+'mask_%s_mthd%i' % (region, mthd)
    mask_idx = MV.array(fm(region_mask))

    if not os.path.exists('outfiles'):
        os.makedirs('outfiles')
    if not os.path.exists('outfiles/%s_%s_mthd%i' % (date, region, mthd)):
        os.makedirs('outfiles/%s_%s_mthd%i' % (date, region, mthd))

    # Assemble monthly data
    g=cdms.open('outfiles/%s_%s_mthd%i/averaged_%s_%s%i_%s.nc' % (date, region, mthd, region, scf_or_wcf, year, source), 'w') 
    YearlyArray = []
    for case_name_idx in case_name:
        fs = cdms.open(cfs_data_path+case_name_idx)
        cfs = MV.array(fs(scf_or_wcf, squeeze=1))
        cfs[cfs<0] = 0.
        cfs[cfs>1] = 1.
        fs.close()

        len_axis = len(cfs.getAxis(0))

        cfs_idx = MV.array(cfs[:] * mask_idx)
        cfs_idx.setAxis(1,lat)
        cfs_idx.setAxis(2,lon)
        new_data = cdutil.averager(cfs_idx, axis='yx')
        YearlyArray = np.r_[YearlyArray, new_data]

    YearlyArray = MV.array(YearlyArray)
    YearlyArray.id = 'averaged_' + region_mask
    g.write(YearlyArray)
    g.close()
    del(cfs_idx)
    del(YearlyArray) 